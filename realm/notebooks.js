function makeDescriptionForm(td){
    var text = td.text();
    td.show();
    td.append('<button>Сохранить</button>');
    var area = td.find('textarea');
    area.val(text)
	.next()
	.click(function (){
		   var doc_holder = td.parent().prev();
		   var doc = doc_holder.data('doc');		   
		   $.ajax({
			      url:'store_description',
			      data:{'_id':doc._id,
				    'descr':area.val()},
			      type:'POST',			      
			      success:function(data){
				  doc['_rev'] = data;
				  alert('Получилось');
			      },
			      error:function(data){
				  alert('Что-то пошло не так :(');
			      }
			  });
	       });
}

function saveDoc(e){
    var tr = $(e.target).parent();
    var doc = tr.data('doc');
    doc['size'] = parseInt(tr.find('input[name="size"]').val());
    doc['performance'] = parseInt(tr.find('input[name="performance"]').val());
    doc['youtube'] = tr.find('input[name="youtube"]').val();
    // doc['proc_vendor'] = parseInt(tr.find('input[name="proc_vendor"]').val());
    // doc['video'] = parseInt(tr.find('input[name="video"]').val());
    // doc['ram'] = parseInt(tr.find('input[name="ram"]').val());
    // doc['hdd'] = parseInt(tr.find('input[name="hdd"]').val());
    // doc['os'] = parseInt(tr.find('input[name="os"]').val());
    if (tr.data('description')){
	doc['description']['comments'] = tr.next().find('textarea').val();
    }    
    $.ajax({
               url:'store_note',
               type:'POST',
               datatype: "json",
               data:{'note':JSON.stringify(doc)},
               success:function(_rev){
                   doc['_rev'] =_rev;
                   tr.data('doc',doc);
                   alert('Получилось!');
               },
               error:function(er){
                   if (er.responseText
                       .match('[0-9abcdef]+-[0-9abcdef]+$'))
                   {
                       doc['_rev'] = er.responseText;
                       tr.data('doc',doc);
                       alert('Получилось!');
                   }
                   else{
                       alert('Что пошло не так! Не удается сохранить!');
                   }
               }
           });
}
function addInput(doc,name){
    var input = $(document.createElement('input')).attr('name',name);
    if (doc[name] != undefined)
        input.val(doc[name]);
    else
        input.val(-1);
    return input;
}

function fillVideos(data){
    var table = $('#videotable');

        var rows = data['rows'].sort(function(el1,el2){
                                               return el1.doc.price-el2.doc.price;
					   });;
        for (var j=0;j<rows.length;j++){
            var doc = rows[j]['doc'];
            var tr = $(document.createElement('tr'));
            var tr1 = $(document.createElement('tr'));
            var name = $(document.createElement('td'));
            name.html(doc['text'] + '<strong>' + doc['_id'] + '</strong> $'+doc.price);
            var description = $(document.createElement('td'))
                .attr('colspan',5)
                .css({'display':'none'});
            if (doc['description']&&doc['description']['comments']){
                description.html('<textarea>' + doc['description']['comments'] + '</textarea>');
		tr.data('description',true);
            }

            var size = $(document.createElement('td'));
            size.append(addInput(doc,'size'));

            var performance = $(document.createElement('td'));
            performance.append(addInput(doc,'performance'));
	    
	    var youtube = $(document.createElement('td'));
            youtube.append(addInput(doc,'youtube'));



            function showdesc(e){
		var target = $(e.target);
		var td = target.parent().next().find('td');
		makeDescriptionForm(td);
                target.text('спрятать описание');
                target.unbind('click').click(hidedesc);
            }
            function hidedesc(e){
                var target = $(e.target);
                target.parent().next().find('td').hide();
                target.text('показать описание');
                target.unbind('click').click(showdesc);
            }
            var open = $(document.createElement('button'))
                .click(showdesc)
                .text('показать описание');
            var save = $(document.createElement('button'))
                .click(saveDoc)
                .text('сохранить');
            tr.append(name)
            .append(size).append(performance)
		.append(youtube)
	        //.append(proc_vendor).append(video).append(ram).append(hdd)
		//.append(os)
                .append(open).append(save);
            tr.data('doc',doc);
            tr1.append(description);
            table.append(tr);
            table.append(tr1);
        }
    

}

$(function(){
      var table = $('#videotable');
      table.html('<tr><td>name</td><td>size</td><td>performance</td><td>youtube</td></tr>');
      //<td>proc_vendor</td><td>video</td><td>ram</td><td>hdd</td><td>os</td>
      $.ajax({
                 url:'notebooks',
                 success:fillVideos
             });
  });