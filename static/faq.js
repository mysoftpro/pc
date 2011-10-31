_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var ta_initial = "Напишите здесь вопрос, пожелание или просьбу. Что угодно.";
var email_initial = "email";
var name_initial = "имя";

head.ready(function(){
	       var faq_template = _.template('<div style="opacity:0" class="faqrecord"><div class="faqauthor">{{author}}</div><div class="faqdate">{{date}}</div><div style="clear:both;"></div><div class="faqbody">{{body}}</div></div>');
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
	       $('#sendfaq').click(function(e){

				       var to_send = {txt:area.val()};
				       if (to_send['txt'] == ta_initial || to_send['txt'].length==0)
					   area.css('border-color','red');
				       else{
					   area.css('border-color','#444');
					   var emailval = email.val();
					   if (emailval!==email_initial)
					       to_send['email'] = emailval;
					   var nameval = name.val();
					   if (nameval!==name_initial)
					       to_send['name'] = nameval;
					   name:
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
							      .animate({'opacity':'1.0'},500);
						      }
						  });
				       }
				       });

	       var form = $('#faq_top').html();
	       var answer  =$(document
			 .createElement('div'))
		   .attr('id','faqanswer')
		   .html(form);
	       answer.find('textarea').val('Напишите здесь комментарий');
	       answer.css({'opacity':'0'});
	       $('.faqlinks a[name="answer"]').click(function(e){
							var target = $(e.target);
							 var pa = target.parent().parent();
							 answer.animate({'opacity':'0'},400);
							 _.delay(function(){
								     pa.append(answer);
								     answer
									 .animate({'opacity':'1.0'},
										  400);},500);
						    });

	   });