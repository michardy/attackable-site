var counter = 0;
con = document.getElementById("console");

var ws = new WebSocket("wss://hijackingprevention.com/demo/console");
ws.onmessage = function (e) {
   document.getElementById("target" + counter).innerHTML += e.data.toString();
};

function evaluate(cmd){
	if (cmd === "help") {
		document.getElementById("target" + counter).innerHTML += 'Type "reset users" to reset the user db<br/>Type "reset posts" to reset the post db<br/>Type "security &lt;on/off&gt;" to change security hardening<br/>';
	} else {
		ws.send(cmd);
	}
}

function getcmd(e){
	if (e.keyCode == 13){
		document.getElementById("cmd" + counter).removeAttribute("contenteditable", false);
		counter++;
		init();
		evaluate(document.getElementById("cmd" + (counter-1)).textContent);
	}
}

function init (){
	con.innerHTML += "<div id=\"target"+counter+"\"></div>";
	con.innerHTML += "&gt;&gt;&gt;&nbsp;<span id=\"cmd"+counter+"\" onkeypress=\"getcmd(event);\" contenteditable=\"true\"></span><br/>";
	document.getElementById("cmd" + counter).focus();
}

init();
