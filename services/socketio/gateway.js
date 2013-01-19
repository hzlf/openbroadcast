var io = require('socket.io').listen(8888);
var redis = require('redis').createClient();

redis.psubscribe('socketio_*');

/*
redis.on('pmessage', function(pattern, channel, key){
	console.log(channel, key);
	io.socket.emmit(channel, key);
})
*/
io.sockets.on('connection', function (socket) {
	
	console.log('io.sockets.on connection');
	
	redis.on('pmessage', function(pattern, channel, key){
		console.log('redis.on pmessage');
		
		key = JSON.parse(key);
		
		
		console.log(channel, key);
		
		console.log('i-route:', key.route);
		
		// socket.emit(key.route, key);
		
		
		socket.emit('chat', key);
		
		// socket.emmit('socketio_news', key);
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
