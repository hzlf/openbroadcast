import unittest
from dgs2.discogs_client.models import Artist, Release
from dgs2.discogs_client.tests import DiscogsClientTestCase
from dgs2.discogs_client.exceptions import HTTPError

class ModelsTestCase(DiscogsClientTestCase):
    def test_artist(self):
        """Artists can be fetched and parsed"""
        a = self.d.artist(1)
        self.assertEqual(a.name, 'Persuader, The')

    def test_release(self):
        """Releases can be fetched and parsed"""
        r = self.d.release(1)
        self.assertEqual(r.title, 'Stockholm')

    def test_master(self):
        """Masters can be fetched and parsed"""
        m = self.d.master(4242)
        self.assertEqual(len(m.tracklist), 4)

    def test_user(self):
        """Users can be fetched and parsed"""
        u = self.d.user('example')
        self.assertEqual(u.username, 'example')
        self.assertEqual(u.name, 'Example Sampleman')

    def test_search(self):
        results = self.d.search('trash80')
        self.assertEqual(len(results), 13)
        self.assertIsInstance(results[0], Artist)
        self.assertIsInstance(results[1], Release)

    def test_fee(self):
        fee = self.d.fee_for(20.5, currency='EUR')
        self.assertEqual(fee.currency, 'USD')
        self.assertAlmostEqual(fee.value, 1.57)

    def test_invalid_artist(self):
        """Invalid artist raises HTTPError"""
        with self.assertRaises(HTTPError):
            self.d.artist(0).name

    def test_invalid_release(self):
        """Invalid release raises HTTPError"""
        with self.assertRaises(HTTPError):
            self.d.release(0).title

    def test_http_error(self):
        """HTTPError provides useful information"""
        with self.assertRaises(HTTPError) as cm:
            self.d.artist(0).name

        self.assertEqual(cm.exception.status_code, 404)
        self.assertEqual('404: Resource not found.', str(cm.exception))

    def test_parent_label(self):
        """Test parent_label / sublabels relationship"""
        l = self.d.label(1)
        l2 = self.d.label(31405)

        self.assertIsNone(l.parent_label)
        self.assertIn(l2, l.sublabels)
        self.assertEqual(l2.parent_label, l)

    def test_master_versions(self):
        """Test main_release / versions relationship"""
        m = self.d.master(4242)
        r = self.d.release(79)
        v = m.versions

        self.assertEqual(len(v), 2)
        self.assertIn(r, v)
        self.assertEqual(r.master, m)

        r2 = self.d.release(3329867)
        self.assertIsNone(r2.master)

    def test_user_writable(self):
        """User profile can be updated"""
        u = self.d.user('example')
        u.name # Trigger a fetch

        method, url, data, headers = self.d._fetcher.requests[0]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/users/example')

        new_home_page = 'http://www.discogs.com'
        u.home_page = new_home_page
        self.assertIn('home_page', u.changes)
        self.assertNotIn('profile', u.changes)

        u.save()

        # Save
        method, url, data, headers = self.d._fetcher.requests[1]
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/users/example')
        self.assertEqual(data, {'home_page': new_home_page})

        # Refresh
        method, url, data, headers = self.d._fetcher.requests[2]
        self.assertEqual(method, 'GET')
        self.assertEqual(url, '/users/example')

    def test_wantlist(self):
        """Wantlists can be manipulated"""
        # Fetch the user/wantlist from the filesystem
        u = self.d.user('example')
        self.assertEqual(len(u.wantlist), 3)

        # Stub out expected responses
        self.m._fetcher.fetcher.responses = {
            '/users/example/wants/5': ('{"id": 5}', 201),
            '/users/example/wants/1': ('', 204),
        }

        # Now bind the user to the memory client
        u.client = self.m

        u.wantlist.add(5)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'PUT')
        self.assertEqual(url, '/users/example/wants/5')

        u.wantlist.remove(1)
        method, url, data, headers = self.m._fetcher.last_request
        self.assertEqual(method, 'DELETE')
        self.assertEqual(url, '/users/example/wants/1')

    def test_delete_object(self):
        """Can request DELETE on an APIObject"""
        u = self.d.user('example')
        u.delete()

        method, url, data, headers = self.d._fetcher.last_request
        self.assertEqual(method, 'DELETE')
        self.assertEqual(url, '/users/example')

    def test_identity(self):
        """OAuth identity returns a User"""
        me = self.d.identity()
        self.assertEqual(me.data['consumer_name'], 'Test Client')
        self.assertEqual(me, self.d.user('example'))


def suite():
    suite = unittest.TestSuite()
    suite = unittest.TestLoader().loadTestsFromTestCase(ModelsTestCase)
    return suite
