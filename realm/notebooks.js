function saveDoc(e){
    var tr = $(e.target).parent();
    var doc = tr.data('doc');
    // doc['hdmi'] = parseInt(tr.find('input[name="hdmi"]').val());
    // doc['dvi'] = parseInt(tr.find('input[name="dvi"]').val());
    // doc['d-sub'] = parseInt(tr.find('input[name="d-sub"]').val());
    doc['size'] = parseInt(tr.find('input[name="size"]').val());
    doc['performance'] = parseInt(tr.find('input[name="performance"]').val());
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
                description.html(doc['description']['comments']);
            }

            var size = $(document.createElement('td'));
            size.append(addInput(doc,'size'));

            var performance = $(document.createElement('td'));
            performance.append(addInput(doc,'performance'));

            function showdesc(e){
                var target = $(e.target);
                target.parent().next().find('td').show();
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
                .append(open).append(save);
            tr.data('doc',doc);
            tr1.append(description);
            table.append(tr);
            table.append(tr1);
        }
    

}

$(function(){
      var table = $('#videotable');
      table.html('<tr><td>name</td><td>size</td><td>performance</td></tr>');
      $.ajax({
                 url:'notebooks',
                 success:fillVideos
             });
  });