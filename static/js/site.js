window.onload = (function(){
	try{
		$(document).ready(function(){
			$.validator.addMethod(
				"nospace", 
				function(value, element) {
					return this.optional(element) || (value.indexOf(' ') == -1)
			},
			$.format("Please enter a single word")
			);
			$("#sidebarForm").validate(
				{
					errorLabelContainer: $("#RegisterErrors"),
					rules: {
						name: { required: true, maxlength: 140, nospace: false},
						account: { required: true, maxlength: 30, nospace: true},
						callsign: {required: false, maxlength: 140, nospace: true}
					},
					messages: {
						name: "Please give your TweetSwarm a snappy name (shorter than 140 characters)",
						account: "Please specify an account for your TweetSwarm to follow, up to thirty characters",
						callsign: "Hashtags can't be more than 140 characters!"
					}
				});
		});
	}catch(e){}});