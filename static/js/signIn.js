$(function(){
	$('#btnSignIn').click(function(){
		$.ajax({
			url: '/validateLogin',
			data: $('#login-nav').serialize(),
			type: 'POST',
			success: function(response) {
				console.log(response);
			},
			error: function(error) {
				console.log(error);
			}
		});
	});
});