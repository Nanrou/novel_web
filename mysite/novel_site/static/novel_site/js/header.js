var jieqiUserId = 0;
var jieqiUserName = '';
var jieqiUserPassword = '';
var jieqiUserGroup = 0;
var jieqiNewMessage = 0;
var jieqiUserVip = 0;
var jieqiUserHonor = '';
var jieqiUserGroupName = '';
var jieqiUserVipName = '';


var timestamp = Math.ceil((new Date()).valueOf()/1000); //当前时间戳，精确到秒
var flag_overtime = -1;
if(document.cookie.indexOf('jieqiUserInfo') >= 0){
	var jieqiUserInfo = get_cookie_value('jieqiUserInfo');
	//document.write(jieqiUserInfo);
	start = 0;
	offset = jieqiUserInfo.indexOf(',', start); 
	while(offset > 0){
		tmpval = jieqiUserInfo.substring(start, offset);
		tmpidx = tmpval.indexOf('=');
		if(tmpidx > 0){
           tmpname = tmpval.substring(0, tmpidx);
		   tmpval = tmpval.substring(tmpidx+1, tmpval.length);
		   if(tmpname == 'jieqiUserId') jieqiUserId = tmpval;
		   else if(tmpname == 'jieqiUserName_un') jieqiUserName = tmpval;
		   else if(tmpname == 'jieqiUserPassword') jieqiUserPassword = tmpval;
		   else if(tmpname == 'jieqiUserGroup') jieqiUserGroup = tmpval;
		   else if(tmpname == 'jieqiNewMessage') jieqiNewMessage = tmpval;
		   else if(tmpname == 'jieqiUserVip') jieqiUserVip = tmpval;
		   else if(tmpname == 'jieqiUserHonor_un') jieqiUserHonor = tmpval;
		   else if(tmpname == 'jieqiUserGroupName_un') jieqiUserGroupName = tmpval;
		}
		start = offset+1;
		if(offset < jieqiUserInfo.length){
		  offset = jieqiUserInfo.indexOf(',', start); 
		  if(offset == -1) offset =  jieqiUserInfo.length;
		}else{
          offset = -1;
		}
	}
	flag_overtime = get_cookie_value('overtime');
}
else {
	delCookie('overtime');
}

function setCookie(c_name,value,expiredays)//设置cookie
{   
    var expiredays=expiredays||30;
    var exdate=new Date();//生成当时的时间
    exdate.setDate(exdate.getDate()+expiredays); //时间加上30天 
    document.cookie=c_name+ "=" +escape(value)+";expires="+exdate.toUTCString()+";";
    //escape是编码字符串（编码URL有专门的encodeURL），toGMTString已经弃用，改成UTC，paths的默认位置就是/
}

function getCookie(c_name)//拿到某个name的值
{
    if (document.cookie.length>0){//若没有cookie则直接返回空
        c_start=document.cookie.indexOf(c_name + "=");//找到目标name的起始位置
        if (c_start!=-1){ 
            c_start=c_start + c_name.length+1;//然后定位到等号的位置
            c_end=document.cookie.indexOf(";",c_start);//从等号位置开始去找最近的分号
            if (c_end==-1) c_end=document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));//substring是按位置截取部分字符串
        } 
    }
    return "";
}

function delCookie(name){//只需要设置 expires 参数为以前的时间即可
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    document.cookie= name + "=;expires="+exp.toGMTString();
}

function get_cookie_value(Name) { //跟getcookie逻辑一样的啊
    var search = Name + "=";
    var returnvalue = ""; 
    if (document.cookie.length > 0) { 
        offset = document.cookie.indexOf(search) 
        if (offset != -1) { 
        offset += search.length 
        end = document.cookie.indexOf(";", offset); 
            if (end == -1) end = document.cookie.length; 
            returnvalue=unescape(document.cookie.substring(offset, end));
　　} 
　} 
　return returnvalue; 
}

function login(){  //need to delete
document.writeln("<div style=\"display:none\" >");
document.writeln("</div>");
document.writeln("<div class=\"ywtop\"><div class=\"ywtop_con\"><div class=\"ywtop_sethome\"><a onClick=\"this.style.behavior='url(#default#homepage)';this.setHomePage('http://www.ranwen.org');\" href=\"#\">将本站设为首页</a></div>");
document.writeln("<div class=\"ywtop_addfavorite\"><a href=\"javascript:window.external.addFavorite(\'http://www.ranwen.org\',\'燃文小说_书友最值得收藏的网络小说阅读网\')\">收藏燃文小说</a></div>");
document.write('<div class="nri">');
if(jieqiUserId != 0 && jieqiUserName != '' && (document.cookie.indexOf('PHPSESSID') != -1 || jieqiUserPassword != '')){
  if(jieqiUserVip == 1) jieqiUserVipName='<span class="hottext">至尊VIP-</span>';
  document.write('Hi,<a href="/userdetail.php?uid='+jieqiUserId+'" target="_top">'+jieqiUserName+'</a>&nbsp;&nbsp;<a href="/modules/article/bookcase.php?uid='+jieqiUserId+'" target="_top">我的书架</a>');
  if(jieqiNewMessage > 0){
	  document.write(' | <a href="/message.php?uid='+jieqiUserId+'&box=inbox" target="_top"><span class=\"hottext\">您有短信</span></a>');
  }else{
	  document.write(' | <a href="/message.php?uid='+jieqiUserId+'&box=inbox" target="_top">查看短信</a>');
  }
  document.write(' | <a href="/userdetail.php?uid='+jieqiUserId+'" target="_top">查看资料</a> | <a href="/logout.php" target="_self">退出登录</a>&nbsp;');
}else{
  var jumpurl="";
  if(location.href.indexOf("jumpurl") == -1){
    jumpurl=location.href;
  }
  document.write('<form name="frmlogin" id="frmlogin" method="post" action="/login.php?do=submit&action=login&usecookie=1&jumpurl="'+jumpurl+'&jumpreferer=1>');
  document.write('<div class="cc"><div class="txt">账号：</div><div class="inp"><input type="text" name="username" id="username" /></div></div>');
  document.write('<div class="cc"><div class="txt">密码：</div><div class="inp"><input type="password" name="password" id="password" /></div></div>');
  document.write('<div class="frii"><input type="submit" class="int" value=" " /></div><div class="ccc"><div class="txtt"><a href="/getpass.php">忘记密码</a></div><div class="txtt"><a href="/register.php">用户注册</a></div></div></form>');
}
 document.write('</div></div></div>');
}

function footer(){  //need to delete
document.writeln("<p>本站所有小说为转载作品，所有章节均由网友上传，转载至本站只是为了宣传本书让更多读者欣赏。</p>");
document.writeln("<p>Copyright &copy; 2015 燃文小说 All Rights Reserved.</p>");
document.writeln("<p>冀ICP备11007602号</p>");
document.writeln("<div style=\"display:none\" >");
document.writeln("<script src=\"http://s11.cnzz.com/z_stat.php?id=1261070902&web_id=1261070902\" language=\"JavaScript\"></script>");
document.writeln("</div>");
}

function panel(){  //need to delete
document.writeln("<form action=\"http://so.ranwen.org/cse/search\" name=\"form\" id=\"sform\" target=\"_blank\" method=\"get\">");
document.writeln("<div class=\"search\">");
document.writeln("<input type=\"hidden\" name=\"s\" value=\"18402225725594290780\">");
document.writeln("<input type=\"hidden\" name=\"ie\" value=\"gbk\">");
document.writeln("<input name=\"q\" type=\"text\" class=\"input\" value=\"输入需要搜索的小说\" onblur=\"if (value ==\'\'){value=\'输入需要搜索的小说\'}\" onfocus=\"if (value ==\'输入需要搜索的小说\'){value =\'\'}\" id=\"wd\"/><span class=\"s_btn\"><input type=\"submit\" value=\" 搜 索 \" class=\"button\"></span>");
document.writeln("</div>");
document.writeln("</form>");
}

//updown
jQuery(document).ready(function($) {
    $body = (window.opera) ? //判断浏览器是不是opera
        (document.compatMode == "CSS1Compat" ? $("html") : $("body")) 
        : $("html,body");
    $("#shang").mouseover(function() {
        up()})
        .mouseout(function() {
            clearTimeout(fq)})  //取消掉那个定时器
        .click(function() {
            $body.animate({scrollTop: 0},400)});
    $("#xia").mouseover(function() {
        dn()})
        .mouseout(function() {
            clearTimeout(fq)})
        .click(function() {
            $body.animate({scrollTop: $(document).height()},400)});
    $("#comt").click(function() {
        $body.animate({scrollTop: $("#content").offset().top},400)});});
function up() {  //一旦启动就进入自调用模式了
    $wd = $(window);
    $wd.scrollTop($wd.scrollTop() - 1);
    fq = setTimeout("up()", 50)}; //每隔50ms就会调用自身
function dn() {
    $wd = $(window);
    $wd.scrollTop($wd.scrollTop() + 1);
    fq = setTimeout("dn()", 50)}; 