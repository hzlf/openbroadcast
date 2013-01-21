var io = require('socket.io').listen(8888);
var redis = require('redis').createClient();

redis.psubscribe('push_*');

/*
redis.on('pmessage', function(pattern, channel, key){
	console.log(channel, key);
	io.socket.emmit(channel, key);
})
*/
io.sockets.on('connection', function (socket) {
	
	console.log('io.sockets.on connection');
	
	redis.on('pmessage', function(pattern, channel, data){
		
		data = JSON.parse(data);
		
		// console.log(channel, data);		
		console.log('i-pattern:', pattern);
		console.log('i-route:', data.route);
		
		socket.emit('push', data);

	})
	
	
/*
  socket.on('ferret', function (name, fn) {
  	console.log('ferret');
  	
    fn('woot');
  });
*/
  
});

/*
io.sockets.on('connection', function (socket) {
  socket.broadcast.emit('user connected');
  socket.broadcast.json.send({ a: 'message' });
});
*/
