$(window).load(function(){  // 页面加载完后就设置cookie
		var tmp = $('#book_name').text() + '  ' + $('#nr_title').text();
		
		setCookie('lastread_title', tmp, 365);
		setCookie('lastread_url', window.location.pathname, 365);
});


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