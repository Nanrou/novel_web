$(window).load(function(){  // 页面加载完后就设置cookie
		var tmp = $('#book_name').text() + '  ' + $('#nr_title').text();
		
		setCookie('lastread_title', tmp, 365);
		setCookie('lastread_url', window.location.pathname, 365);
});

function setSize(size) {  // 设置字体大小 
	$('#fontbig').css("background-color", '#ECF0F0');
	$('#fontmiddle').css("background-color", '#ECF0F0');
	$('#fontsmall').css("background-color", '#ECF0F0');
	if (size == 'big'){
		$("#nr").css("fontSize", '26px');
		$('#fontbig').css("background-color", '#A7A7A7');
	}else if (size == 'middle'){
		$("#nr").css("fontSize", '22px');
		$('#fontmiddle').css("background-color", '#A7A7A7');
	}else {
		$("#nr").css("fontSize", '16px');
		$('#fontsmall').css("background-color", '#A7A7A7');
	}
	setCookie("m_fontsize", size, 365);
}

function setHuyan() {  // 护眼模式
	$("#nr").css("color", '#000');
	$("#nr_title").css("color", '#000');
	$("#lightdiv").css("background-color", '#ECF0F0');
	$("#lightdiv").text('关灯');
	setCookie("m_yejian", 0, 365);

	var switch_ = getCookie('m_huyan')
	if (switch_ == 1){
		$("#nr_body").css("background-color", '#FBF6EC');
		$("#huyandiv").css("background-color", '#ECF0F0');
		setCookie("m_huyan", 0, 365);
	}
	else {
		$("#nr_body").css("background-color", '#DCECD2');
		$("#huyandiv").css("background-color", '#A7A7A7');
		setCookie("m_huyan", 1, 365);
	}
}

function setYejian() {  // 夜间模式
	$("#huyandiv").css("background-color", '#ECF0F0');
	setCookie("m_huyan", 0, 365);

	var switch_ = getCookie('m_yejian')
	if (switch_ == 1){
		$("#nr_body").css("background-color", '#FBF6EC');
		$("#nr").css("color", '#000');
		$("#nr_title").css("color", '#000');
		$("#lightdiv").css("background-color", '#ECF0F0');
		$("#lightdiv").text('关灯');
		setCookie("m_yejian", 0, 365);
	}
	else {
		$("#nr_body").css("background-color", '#32373B');
		$("#nr").css("color", '#CCCCCC');
		$("#nr_title").css("color", '#CCCCCC');
		$("#lightdiv").css("background-color", '#A7A7A7');
		$("#lightdiv").text('开灯');
		setCookie("m_yejian", 1, 365);
	}
}

$(document).ready(function(){  // 页面初始化
	var size = getCookie("m_fontsize");
	if (size){
		setSize(size);
	}else {
		setSize('middle');
	};
	var huyan = getCookie("m_huyan");
	if (huyan==1){
		setCookie("m_huyan", 0, 365);
		setHuyan();
	};
	var yejian = getCookie("m_yejian");
	if (yejian==1){
		setCookie("m_yejian", 0, 365);
		setYejian();
	};
})