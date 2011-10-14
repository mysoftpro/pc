function addInput(doc,name){
    var input = $(document.createElement('input')).attr('name',name);
    console.log(input);
    if (doc[name])
        input.val(doc[name]);
    else
        input.val(-1);
    return input;
}

function fillMothers(data){
    var table = $('#mothertable');
    for (var i=0;i<data.length;i++){
        var rows = data[i][1]['rows'];
        for (var j=0;j<rows.length;j++){
            var doc = rows[j]['doc'];
            var tr = $(document.createElement('tr'));
            var tr1 = $(document.createElement('tr'));
            var name = $(document.createElement('td'));
            name.html(doc['text']);
            var description = $(document.createElement('td'))
                .attr('colspan',5)
                .css({'display':'none'});
            if (doc['description']&&doc['description']['comments']){
                description.html(doc['description']['comments']);
            }

            var video = $(document.createElement('td'));
            video.append(addInput(doc,'video'));

            var ramslots = $(document.createElement('td'));
	    ramslots.append(addInput(doc,'ramslots'));

            var maxram = $(document.createElement('td'));
	    maxram.append(addInput(doc,'maxram'));

            var open = $(document.createElement('button'))
                .click(function(e){$(e.target).parent().next().find('td').show();})
                .text('показать описание');
            var save = $(document.createElement('button'))
                .click(function(e){$(e.target).parent().next().find('td').show();})
                .text('сохранить');
            tr.append(name).append(video).append(ramslots).append(maxram)
                .append(open).append(save);
            tr1.append(description);
            table.append(tr);
            table.append(tr1);
        }
    }

}

$(function(){
      var table = $('#mothertable');
      table.html('<tr><td>name</td><td>video</td><td>ramslots</td><td>maxram</td></tr>');
      $.ajax({
                 url:'mothers',
                 success:fillMothers
             });
  });