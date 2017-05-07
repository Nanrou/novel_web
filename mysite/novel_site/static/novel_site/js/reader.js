( function() {//拿浏览器的UA和version
	var ua = navigator.userAgent.toLowerCase();
	var is = (ua.match(/\b(chrome|opera|safari|msie|firefox)\b/) || [ '',
			'mozilla' ])[1];
	var r = '(?:' + is + '|version)[\\/: ]([\\d.]+)';
	var v = (ua.match(new RegExp(r)) || [])[1];
	jQuery.browser.is = is;
	jQuery.browser.ver = v;
	jQuery.browser[is] = true;

})();

var speed = 5;
var autopage;// = $.cookie("autopage");
var night;
var timer;
var temPos=1;

$(document).ready(function(){//初始化页面可选部分
	if(typeof(nextpage) != "undefined" ) {//应该要修改这部分逻辑，nextpage不存在，后面所有的都可以加上默认值
                            //没必要为所有的可选都设置cookie
		nextpage = nextpage;
		autopage = getCookie("autopage");
		
		sbgcolor = getCookie("bcolor");
		setBGColor(sbgcolor);
		
		font = getCookie("font");
		setFont(font);
		
		size = getCookie("size");
		setSize(size);
		
		fontcolor = getCookie("fontcolor");
		setColor(fontcolor);
		
		width = getCookie("width");
		setWidth(width);
		
		speed = getCookie("scrollspeed");
		
		if(autopage==1) {
			$('#autopage').attr("checked",true);//设置checkerd为ture
			speed = getCookie("scrollspeed");
			scrollwindow();
		}
		
		night = getCookie('night');
		if(night==1) {
			$("#night").attr('checked',true);
			setNight();
		}
		document.onmousedown=sc;
		document.ondblclick=scrollwindow;
	}
});

if (getCookie("bgcolor") != '') {
    wrapper.style.background = getCookie("bgcolor");
    document.getElementById("bcolor").value = getCookie("bgcolor")
}

function changebgcolor(id) {
    wrapper.style.background = id.options[id.selectedIndex].value;
    setCookie("bgcolor", id.options[id.selectedIndex].value, 365)
}

function setBGColor(sbgcolor){
	$('#wrapper').css("background-color",sbgcolor);
	setCookie("bcolor",sbgcolor,365);
}

function setColor(fontcolor) {
	$("#content").css("color",fontcolor);
	setCookie("fontcolor",fontcolor,365);
}

function setSize(size) {
	$("#content").css("fontSize",size);
	setCookie("size",size,365);
}
function setFont(font) {
	$("#content").css("fontFamily",font);
	setCookie("font",font,365);
}
function setWidth(width){
	$('#content').css("width",width);
	setCookie("width",width,365);
}
function setNight(){
	if($("#night").attr('checked')==true) {
		$('div').css("backgroundColor","#111111");
		$('div,a').css("color","#939392");
		setCookie("night",1,365);
	} else {
		$('div').css("backgroundColor","");
		$('div,a').css("color","");
		setCookie("night",0,365);
	}
}

function scrolling() 
{  
	var currentpos=1;
	if($.browser.is=="chrome" |document.compatMode=="BackCompat" ){
		currentpos=document.body.scrollTop;
	}else{
		currentpos=document.documentElement.scrollTop;
	}

	window.scroll(0,++currentpos);
	if($.browser.is=="chrome" || document.compatMode=="BackCompat" ){
		temPos=document.body.scrollTop;
	}else{
		temPos=document.documentElement.scrollTop;
	}

	if(currentpos!=temPos){
        ///msie/.test( userAgent )
        var autopage = getCookie("autopage");
        if(autopage==1&&/nextpage/.test( document.referrer ) == false) location.href=nextpage;
		sc();
	}
}

function scrollwindow(){ //设置定时任务：滚屏
	timer=setInterval("scrolling()",250/speed);
}

function sc(){ //取消定时任务
	clearInterval(timer); 
}

function setSpeed(ispeed){ 
	if(ispeed==0)ispeed=5;
	speed=ispeed;
	setCookie("scrollspeed",ispeed,365);
}

function setAutopage(){//自动翻页
	if($('#autopage').is(":checked") == true){
		$('#autopage').attr("checked",true);	
		setCookie("autopage",1,365);
	}else{
		$('#autopage').attr("checked",false);
		setCookie("autopage",0,365);
	}
}

var timestamp = Math.ceil((new Date()).valueOf()/1000); //当前时间戳
var flag_overtime = -1;
		
function LastRead(){this.bookList="bookList"}
LastRead.prototype={
	set:function(bid,tid,title,texttitle,author,sortname){
		if(!(bid&&tid&&title&&texttitle&&author&&sortname))return;
		var v=bid+'#'+tid+'#'+title+'#'+texttitle+'#'+author+'#'+sortname;
		this.setItem(bid,v);
		this.setBook(bid)
	},
	get:function(k){
		return this.getItem(k)?this.getItem(k).split("#"):"";				
	},
	remove:function(k){
		this.removeItem(k);
		this.removeBook(k)	
	},
	setBook:function(v){
		var reg=new RegExp("(^|#)"+v);
		var books =	this.getItem(this.bookList);
		if(books==""){
			books=v
			}
		 else{
			 if(books.search(reg)==-1){
				 books+="#"+v	 
				 }
			 else{
				  books.replace(reg,"#"+v)
				 } 
			 }
		this.setItem(this.bookList,books)		
	},
	getBook:function(){
		var v=this.getItem(this.bookList)?this.getItem(this.bookList).split("#"):Array();
		var books=Array();
		if(v.length){
			for(var i=0;i<v.length;i++){
				var tem=this.getItem(v[i]).split('#');
				if (tem.length>3)books.push(tem);
				}
			}
		return books
	},
	removeBook:function(v){
	    var reg=new RegExp("(^|#)"+v);
		var books=this.getItem(this.bookList);
		if(!books){
			books=""
			}
		 else{
			 if(books.search(reg)!=-1){
			      books=books.replace(reg,"")
				 }
			 }
		this.setItem(this.bookList,books)
	},
	setItem:function(k,v){
		if(!!window.localStorage){
			localStorage.setItem(k,v);	
		}
		else{
			var expireDate=new Date();
			  var EXPIR_MONTH=30*24*3600*1000;		
			  expireDate.setTime(expireDate.getTime()+12*EXPIR_MONTH)
			  document.cookie=k+"="+encodeURIComponent(v)+";expires="+expireDate.toGMTString()+"; path=/";	
		}
	},
	getItem:function(k){
		var value=""
		var result=""
		if(!!window.localStorage){
			result=window.localStorage.getItem(k);
			 value=result||"";
		}
		else{
			var reg=new RegExp("(^| )"+k+"=([^;]*)(;|\x24)");
			var result=reg.exec(document.cookie);
			if(result){
				value=decodeURIComponent(result[2])||""}
		}
		return value
	},
	removeItem:function(k){
		if(!!window.localStorage){
		 window.localStorage.removeItem(k);
		}
		else{
			var expireDate=new Date();
			expireDate.setTime(expireDate.getTime()-1000)
			document.cookie=k+"= "+";expires="+expireDate.toGMTString()
		}
	},
	removeAll:function(){
		if(!!window.localStorage){
		 window.localStorage.clear();
		}
		else{
		var v=this.getItem(this.bookList)?this.getItem(this.bookList).split("#"):Array();
		var books=Array();
		if(v.length){
			for( i in v ){
				var tem=this.removeItem(v[k])
				}
			}
			this.removeItem(this.bookList)
		}
	}
}
window.lastread = new LastRead();