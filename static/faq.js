_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var ta_initial = "Напишите здесь вопрос, пожелание или просьбу. Что угодно.";
var taa_initial = "Напишите здесь комментарий.";
var email_initial = "email";
var name_initial = "имя";
var answer_initial = "имя";

head.ready(function(){
	       var faq_template = _.template('<div style="opacity:0" class="faqrecord"><div class="faqauthor">{{author}}</div><div class="faqdate">{{date}}</div><div style="clear:both;"></div><div class="faqbody">{{body}}</div><div class="faqlinks"><a name="answer">ответить</a></div></div>');
	       var area = $('#faq_top textarea');
	       var email = $('#faq_top input[name="email"]');
	       var name = $('#faq_top input[name="name"]');
	       var clear = function(txt){
		   return function(e){
		       
		       var target = $(e.target);
		       if (target.val() == txt)
			   target.val('');
		   };
	       };
	       area.click(clear(ta_initial));
	       email.click(clear(email_initial));
	       name.click(clear(name_initial));
	       function send(e){		   
		   var target = $(e.target);		   
		   while (!target.attr('id') &&
			  target.attr('id')!=='faq_top' &&
			  target.attr('id')!=='faqanswer'){
		       target = target.parent();
		   }
		   var _area,_email,_name;
		   var parent;
		   if (target.attr('id')=='faq_top'){
		       _area = area;
		       _email = email;
		       _name = name;
		   }
		   else{
		       _area = target.find('textarea');
		       _email = target.find('input[name="email"]');
		       _name = target.find('input[name="name"]');
		       parent = target.parent().attr('id');
		   }
		   var to_send = {txt:_area.val()};
		   if (to_send['txt'] == ta_initial || to_send['txt'].length==0
		       || to_send['txt']==answer_initial)
		       area.css('border-color','red');
		   else{
		       area.css('border-color','#444');
		       var emailval = _email.val();
		       if (emailval!==email_initial)
			   to_send['email'] = emailval;
		       var nameval = _name.val();
		       if (nameval!==name_initial)
			   to_send['name'] = nameval;
		       if (parent)
			   to_send['parent'] =parent;
		       $.ajax({
				  url:'/storefaq',
				  data:to_send,
				  type:'post',
				  success:function(data){
				      var d = new Date();
				      var _date = d.getDate()+'.';
				      _date +=+d.getMonth()+1+'.';
				      _date +=+d.getFullYear()+'';
				      var middle = $('#faq');
				      var author = $.cookie('pc_user');
				      if (to_send['name'])
					  author = to_send['name'];
				      middle.children().first()
					  .before(faq_template(
						      {'body':to_send['txt'],
						       'author':author,
						       'date':_date}));
				      middle
					  .children()
					  .first()
					  .animate({'opacity':'1.0'},500).find('a').click(postAnswer);
				  }
			      });
		   }
	       };
	       $('.sendfaq').click(send);

	       var form = $('#faq_top').html();
	       var answer  =$(document
			 .createElement('div'))
		   .attr('id','faqanswer')
		   .html(form);
	       answer.find('textarea').val(taa_initial).click(clear(taa_initial));
	       answer.find('input[name="email"]').click(clear(email_initial));
	       answer.find('input[name="name"]').click(clear(name_initial));
	       answer.css({'opacity':'0'});
	       function postAnswer(e){
		   var target = $(e.target);
		   var pa = target.parent().parent();
		   answer.animate({'opacity':'0'},400);
		   answer.find('.sendfaq').unbind('click')
		       .click(send);
		   _.delay(function(){
			       pa.append(answer);
			       answer
				   .animate({'opacity':'1.0'},
					    400);},500);
		   
	       }
	       $('.faqlinks a[name="answer"]').click(postAnswer);

	   });