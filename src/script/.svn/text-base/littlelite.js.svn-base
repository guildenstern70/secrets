/**
 * Copyright 2009 LittleLite Software.
 * Need Prototype library v.1.6 or greater
 * 
 * v.0.5.1078
 * 
 */


function gup(name) {
	name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	var regexS = "[\\?&]" + name + "=([^&#]*)";
	var regex = new RegExp(regexS);
	var results = regex.exec(window.location.href);
	if (results == null)
		return "";
	else
		return results[1];
}

function menuload() {
	var message = gup('msg');
	if (message.length > 0) {
		flash_message(message.replace(/\+/g, ' '));
	}
}

function checkQuota() {
	var contOk = true;
	var msgs = parseInt($F('nrmsgs'));
	var qt = parseInt($F('quota'));
	if (msgs > qt) {
		alert('You exceeded quota (' + msgs + '). Please delete messages before continuing.');
		contOk = false;
	}
	return contOk;
}

function checkAll() {
	//console.debug('Checking all')	
	var setoption = 0;
	if (document.forms['messageList'].selectAll.checked)
		setoption = 1;
	checkAllAs(setoption);
}

function checkedItems() {
	var form = $('messageList');
	var checks = $A(form.getInputs('checkbox','xssl')); // -> only checkbox inputs
	var count = 0;
	checks.each(function(check) {
			if (check.checked) count++;
		}
	);
	return count;
}

function checkAllAs(checked) {
	var field = document.forms['messageList'].xssl;
	for (var i = 0; i < field.length; i++)
		field[i].checked = checked;
}

function youSure() {
	return window.confirm("Really delete message(s)?");
}

function youShredSure() {
	return window.confirm("The message(s) will be erased from database. Continue?");
}

function hide_flashmessage() {
	$('flashmessage').hide();
}

function flash_message(message) {
	$('flashmessage').show();
	$('flashmessagespace').update(unescape(message));
}

function decrypt_request_pt(message, password, algo) {

	//console.log("Welcome to decrypt request");

	var params = new Array();
	params.push(message);
	params.push(password);
	params.push(algo);
	var body = Object.toJSON(params);

	//console.debug("Body request is: " + body);

	var oOptions = {
		method : 'post',
		contentType : 'text/xml',
		parameters : body,
		onSuccess : function(oXHR, oJson) {
		//console.log("Received response OK");
		updateMessage(oXHR.responseText);
	},
	onFailure : function(oXHR, oJson) {
		//console.warn("Received KO");
		updateMessage('[Wrong password or method?]');
	}
	};

	//console.log('Calling Request...');
	var request = new Ajax.Request('/view', oOptions);
	//console.log('...done.');
}

function updateMessage(dcrptMessage) {
	
	try {
		$('reply_li').show();
		$('forward_li').show();
		$('archive_li').show();
		$('shred_li').show();
		$('delete_li').show();
		$('decrypt_li').hide();
		$('messagelabel').update('Decrypted Message');
	} catch (e) {
		//Buttons_links may or may not be there
	}

	hide_flashmessage();
	//console.log('Updating with response: '+dcrptMessage);
	$('message').value = dcrptMessage.evalJSON();
}

function validate_required(field, alerttxt) {
	with (field) {
		if (value == null || value == "") {
			alert(alerttxt);
			return false;
		} else {
			return true;
		}
	}
}

function validate_email(field, alerttxt) {
	with (field) {
		apos = value.indexOf("@");
		dotpos = value.lastIndexOf(".");
		if (apos < 1 || dotpos - apos < 2) {
			alert(alerttxt);
			return false;
		} else {
			return true;
		}
	}
}

function validate_form(thisform) {
	//console.debug("Entered validate form");
	with (thisform) {
		
		if (subject.value == "Warning: subject will not be encrypted") {
			subject.value = "";
		}
		
		if (validate_required(subject, "You must enter a subject") == false) {
			subject.focus();
			return false;
		}

		if (validate_required(message, "You must enter the text of the message") == false) {
			message.focus();
			return false;
		}

		if (validate_email(receiver, "Please enter a valid e-mail address") == false) {
			receiver.focus();
			return false;
		}
	}

	return true;
}

function menucommander(command) {
	
	var cmd = $('mode');
	cmd.value = command;
	
	var numberOfCheckedItems = checkedItems();
	
	if (command.startsWith('mt')) {			
		if (numberOfCheckedItems == 0)
			return false;
	}
	
	switch (command) {
		case 'compose':
			if (!checkQuota())
				return false;
			break;
			
		case 'archive':
			if (numberOfCheckedItems == 0)
				return false;
			break;
			
		case 'delete':
			if (numberOfCheckedItems == 0)
				return false;
			if ($F('whatFolder') == 'trash') {
				if (!youSure())
					return false;
			}
			break;
			
		case 'shred':
			if (numberOfCheckedItems == 0)
				return false;
			if (!youShredSure())
				return false;
			break;
			
		case 'emptytrash':
			if (!youSure())
				return false;
			else {
				checkAllAs(1);
				cmd.value = 'delete';
			}
			break;
			
			
		default:
	}
	
	document.messageList.submit();
}

function commander(command) {
	var cmd = $('mode');
	cmd.value = command;
	
	if (command == 'shred')
		if (!youShredSure())
			return false;
	
	document.formMessage.submit();
}

function saveDraft() {
	var cmd = document.getElementById("mode");
	cmd.value = 'savedraft';
	openpassword(0);
	return false;
}

function decryptDraft() {
	var decryptBtn = document.getElementById("decryptdraft");
	decryptBtn.value = "Encrypt & Send";
	var cmd = document.getElementById("mode");
	cmd.value = 'decryptdraft';
	openpassword(2);
	return false;
}

function openpassword(setmode) {

	/* Setmode = 0 -> Encryption, submit form with retype of password
	   Setmode = 1 -> Decryption, AJAX decrypt
	   Setmode = 2 -> Encryption, submit form asking for just one password */

	if (!validate_form(document.formMessage))
		return false;
	   
	$('nav').hide();

	//console.debug("Entered open password");
	//console.debug("Setmode is " + setmode);

	flash_mex = "";

	if (setmode < 1) {
		flash_mex = "Encrypting message...";
		pwdwindow = dhtmlmodal.open('Password', 'iframe',
				'static/setpassword.html', 'Password',
				'width=350px,height=210px,center=1,resize=0,scrolling=0');
	} else {
		pwdwindow = dhtmlmodal.open('Password', 'iframe',
				'static/password.html', 'Password',
				'width=350px,height=140px,center=1,resize=0,scrolling=0');
	}

	if (flash_mex.length > 0)
		flash_message(flash_mex);

	pwdwindow.onclose = function() {
		var thepwd = this.contentDoc.getElementById("password1").value; //contentDoc!
		//console.debug("Password is [" + thepwd + "]");
		$('secretPassword').value = thepwd;
		var messageCtrl = $('message');
		if (setmode != 1) {
			messageCtrl.readOnly = "true";
			messageCtrl.className = "greyed"
			//console.debug("Submitting form");
			document.formMessage.submit();
		} else {
			//console.debug("Decrypting message...");
			var algo = $F('encryptionAlgo');
			var message = messageCtrl.value;
			messageCtrl.value = "...";
			flash_message('Decryption in process...');
			decrypt_request_pt(message, thepwd, algo);
		}
		$('nav').show();
		return true;
	};

}
