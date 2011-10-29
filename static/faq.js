_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};
var ta_initial = "Напишите здесь вопрос, пожелание или просьбу. Что угодно.";
var in_initial = "email";


head.ready(function(){
	       var faq_template = _.template('<div style="opacity:0" class="faqrecord"><div class="faqauthor">{{id}}</div><div class="faqdate">{{date}}</div><div style="clear:both;"></div><div class="faqbody">{{body}}</div></div>');
	       var area = $('#faq_top textarea');	       
	       var email = $('#faq_top input');
	       var clear = function(txt){
		   return function(e){
		       var target = $(e.target);
		       if (target.val() == txt)
			   target.val('');
		   };
	       };
	       area.click(clear(ta_initial));
	       email.click(clear(in_initial));
	       $('#sendfaq').click(function(e){
				       var to_send = {txt:area.val(),email:email.val()};
				       if (to_send['txt'] == ta_initial || to_send['txt'].length==0)
					   area.css('border-color','red');
				       else{
					   area.css('border-color','#444');
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
							  middle.children().first()
							      .before(faq_template(
									  {'body':to_send['txt'],
									   'id':data,
									   'date':_date}));
							  middle
							      .children()
							      .first()
							      .animate({'opacity':'1.0'},500);
						      }
						  });
				       }
				       });

	   });