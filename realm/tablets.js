function makeDescriptionForm(td){
    var text = td.html();
    td.show();
    td.append('<textarea></textarea><button>Сохранить</button>');
    var area = td.find('textarea');
    area.val(text)
	.next()
	.click(function (){
		   var doc_holder = td.parent().prev();
		   var doc = doc_holder.data('doc');
		   console.log('before');
		   console.log(doc['_rev']);
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
    doc['vendor'] = tr.find('input[name="vendor"]').val();
    doc['model'] = tr.find('input[name="model"]').val();
    doc['os'] = tr.find('input[name="os"]').val();
    doc['screen'] = tr.find('input[name="screen"]').val();
    doc['resolution'] = tr.find('input[name="resolution"]').val();
    doc['memory'] = tr.find('input[name="memory"]').val();
    doc['flash'] = tr.find('input[name="flash"]').val();
    doc['rank'] = tr.find('input[name="rank"]').val();
    doc['youtube'] = tr.find('input[name="youtube"]').val();

    $.ajax({
	       url:'store_tablet',
	       type:'POST',
	       datatype: "json",
	       data:{'mother':JSON.stringify(doc)},
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

function fillMothers(data){
    var table = $('#mothertable');
    for (var i=0;i<data.length;i++){
        var rows = data[i][1]['rows'].sort(function(el1,el2){
                                               return el1.doc.price-el2.doc.price;
					   });
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
                description.html(doc['description']['comments']);
            }

            var vendor = $(document.createElement('td'));
            vendor.append(addInput(doc,'vendor'));

            var model = $(document.createElement('td'));
	    model.append(addInput(doc,'model'));

            var os = $(document.createElement('td'));
	    os.append(addInput(doc,'os'));

            var screen = $(document.createElement('td'));
	    screen.append(addInput(doc,'screen'));

            var resolution = $(document.createElement('td'));
	    resolution.append(addInput(doc,'resolution'));

	    var memory = $(document.createElement('td'));
	    memory.append(addInput(doc,'memory'));
	    
	    var flash = $(document.createElement('td'));
	    flash.append(addInput(doc,'flash'));


	    var rank = $(document.createElement('td'));
	    rank.append(addInput(doc,'rank'));

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
            tr.append(name).append(vendor).append(model).append(os)
	    .append(screen).append(resolution).append(memory).append(flash).append(rank).append(youtube)
                .append(open).append(save);	    
	    tr.data('doc',doc);
	    //console.log(tr.data('doc')._id);
            tr1.append(description);
            table.append(tr);
            table.append(tr1);
        }
    }

}

$(function(){
      var table = $('#mothertable');
      table.html('<tr><td>name</td><td>vendor</td><td>model</td><td>os</td><td>screen</td><td>resolution</td><td>memory</td><td>flash</td><td>rank</td><td>youtube</td></tr>');
      $.ajax({
                 url:'tablets',
                 success:fillMothers
             });
  });