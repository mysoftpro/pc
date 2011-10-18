$(function(e){
      var splitted = document.location.search.split('=');
      if (splitted.length!=2 || splitted[0]!='?id')
          return;
      var _id = splitted[1];
      $('#sign').css({'background-image':'url("/admin/sign.jpg")'});
      $('#stamp').css({'background-image':'url("/admin/stamp.jpg")'});
      $.ajax({
                 url:'/admin/warranty',
                 data:{'_id':_id},
                 success:function(data){
                     if (data == 'fail'){
                         alert('Что-то пошло не так!');
                         return;
                     }
		     var table = $('#components');
                     for (var i=0;i<data['items'].length;i++){
                         var tr = $(document.createElement('tr'));
			 var no = $(document.createElement('td'));
			 no.text(i);
			 var name = $(document.createElement('td'));
			 name.text(data['items'][i]['name']);
			 var count = $(document.createElement('td'));
			 count.text(data['items'][i]['pcs']);
			 var fac = $(document.createElement('td'));
			 fac.text(data['items'][i]['factory']);
			 var war = $(document.createElement('td'));
			 war.text(data['items'][i]['warranty']);
			 tr.append(no);
			 tr.append(name);
			 tr.append(count);
			 tr.append(fac);
			 tr.append(war);
			 table.append(tr);			 
                     }
                 }
             });

  });