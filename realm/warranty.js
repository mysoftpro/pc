_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

$(function(e){
      var splitted = document.location.search.split('=');
      if (splitted.length!=2 || splitted[0]!='?id')
          return;
      var _id = splitted[1];
      $('#number').text(parseInt(_id, 16));
      var _date = new Date();
      $('#year').text(_date.getFullYear());
      $('#month').text(_date.getMonth()+1);
      $('#day').text(_date.getDate());
      // $('#sign').css({'background-image':'url("/admin/sign.jpg")'});
      // $('#stamp').css({'background-image':'url("/admin/stamp.jpg")'});
      $.ajax({
                 url:'/admin/warranty',
                 data:{'_id':_id},
                 success:function(data){
                     if (data == 'fail'){
                         alert('Что-то пошло не так!');
                         return;
                     }
                     var table = $('#components');
		     var tottal = 0;
                     for (var i=0;i<data['items'].length;i++){
                         var tr = $(document.createElement('tr'));
                         var no = $(document.createElement('td'));
                         no.css('text-align','center');
                         no.text(i+1);
                         var name = $(document.createElement('td'));
                         name.html(data['items'][i]['name']);
                         var count = $(document.createElement('td'));
                         count.css('text-align','center');
                         count.text(data['items'][i]['pcs']);

                         var fac = $(document.createElement('td'));

                         var war = $(document.createElement('td'));                         
			 if (document.location.href.match('warranty')){
                             fac.text(data['items'][i]['factory']);
                             war.text(data['items'][i]['warranty']);
                         }
                         else{
			     var price = data['items'][i]['price'];
			     var pcs =data['items'][i]['pcs']; 
                             fac.text(price);
                             war.text(price*pcs);
			     tottal += price*pcs;
                         }
			 tr.append(no);
                         tr.append(name);
                         tr.append(count);
                         tr.append(fac);
                         tr.append(war);                         
                         table.append(tr);
                     }
		     if (tottal>0){	
			 table.append(_.template('<tr><td colspan="5" class="total">Итого: {{tottal}} р.</td></tr>',
						 {tottal:tottal}));
			 var b = $('body');
			 b.append('<div style="margin-top:300px;">&nbsp;</div>');
			 b.append(b.html());
		     }
                 }
             });

  });