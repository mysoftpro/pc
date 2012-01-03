function saveDoc(e){
    var tr = $(e.target).parent();
    var doc = tr.data('doc');
    doc['chip'] = tr.find('input[name="chip"]').val();
    doc['vendor'] = tr.find('input[name="vendor"]').val();
    doc['year'] = tr.find('input[name="year"]').val();
    doc['power'] = tr.find('input[name="power"]').val();
    doc['cores'] = tr.find('input[name="cores"]').val();
    doc['memory'] = tr.find('input[name="memory"]').val();
    doc['memory_ammo'] = tr.find('input[name="memory_ammo"]').val();

    // doc['hdmi'] = parseInt(tr.find('input[name="hdmi"]').val());
    // doc['dvi'] = parseInt(tr.find('input[name="dvi"]').val());
    // doc['d-sub'] = parseInt(tr.find('input[name="d-sub"]').val());
    doc['crossfire'] = parseInt(tr.find('input[name="crossfire"]').val());
    doc['sli'] = parseInt(tr.find('input[name="sli"]').val());
    $.ajax({
	       url:'store_video',
	       type:'POST',
	       datatype: "json",
	       data:{'video':JSON.stringify(doc)},
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
    for (var i=0;i<data.length;i++){
	var rows = data[i][1]['rows'].sort(function(el1,el2){
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

	    
	    var chip = $(document.createElement('td'));
	    chip.append(addInput(doc,'chip'));
	    chip.find('input').css('width','60px');

	    var vendor = $(document.createElement('td'));
	    vendor.append(addInput(doc,'vendor'));
	    vendor.find('input').css('width','60px');



	    var year = $(document.createElement('td'));
	    year.append(addInput(doc,'year'));
	    //year.find('input').css('width','60px');

	    var power = $(document.createElement('td'));
	    power.append(addInput(doc,'power'));
	    //power.find('input').css('width','60px');


	    var cores = $(document.createElement('td'));
	    cores.append(addInput(doc,'cores'));
	    //cores.find('input').css('width','60px');


	    var memory = $(document.createElement('td'));
	    memory.append(addInput(doc,'memory'));
	    //memory.find('input').css('width','60px');

	    var memory_ammo = $(document.createElement('td'));
	    memory_ammo.append(addInput(doc,'memory_ammo'));
	    //memory.find('input').css('width','60px');




	    // var hdmi = $(document.createElement('td'));
	    // hdmi.append(addInput(doc,'hdmi'));

	    // var dvi = $(document.createElement('td'));
	    // dvi.append(addInput(doc,'dvi'));

	    // var dsub = $(document.createElement('td'));
	    // dsub.append(addInput(doc,'d-sub'));

	    var crossfire = $(document.createElement('td'));
	    crossfire.append(addInput(doc,'crossfire'));

	    var sli = $(document.createElement('td'));
	    sli.append(addInput(doc,'sli'));

	    var stock = $(document.createElement('td'));
	    stock.append(addInput(doc,'stock1'));

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
	    .append(crossfire).append(sli).append(chip).append(vendor).append(year).append(power)
		.append(cores).append(memory).append(memory_ammo).append(stock)
		.append(open).append(save);//.append(hdmi).append(dvi).append(dsub)
	    tr.data('doc',doc);
	    tr1.append(description);
	    table.append(tr);
	    table.append(tr1);
	}
    }
    table.before('<div><input id="lowstock" style="width:250px;" value="low stock sli and crossfire" name="lowstocksli" type="button"/></div>');
    $('#lowstock').click(function(e){
			     var rows = _($('tr').toArray());
			     rows.each(function(row){
					   var tds = $(row).find('td').toArray().reverse();
					   var td = $(tds[0]);
					   var stock = td.find('input');//.val();
					   var ammo = parseInt(stock.val());
					   var cross = parseInt(td.prev().find('input').val());
					   var sli = parseInt(td.prev().prev().find('input').val());
					   if (sli+cross>0){
					       if(ammo<=1)
						   stock.css('border','3px solid red');
					       else
						   stock.css('border','3px solid green');
					   }
				       });

			 });
}

$(function(){
      var table = $('#videotable');
      table.html('<tr><td>name</td><td>crossfire</td><td>_s_l_i</td><td>chip</td><td>vendor</td>  <td>year</td><td>power</td><td>cores</td><td>memory</td><td>memory_ammo</td><td>stock</td></tr>');
      $.ajax({
		 url:'videos',
		 success:fillVideos
	     });
  });