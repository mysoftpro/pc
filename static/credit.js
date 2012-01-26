_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

function recalculate(e){
    var tot = $('#total');var total;
    if (tot[0].tagName.toLowerCase()=='input')
	total = parseInt($('#total').val());
    else
	total = parseInt($('#total').text());
    var m = parseInt($('#monthes').val());
    var k;
    var cache = parseInt($('#cache').val());
    if (!cache)cache = 0;
    if (cache >= total/5){
	k= monthly['20'][m];
    }
    else if(cache >= total/10){
	 k= monthly['10'][m];
    }
    else{
	k= monthly['0'][m];
    }
    var monthly_pay = parseInt((total-cache)*k*100+0.01)/100;
    $('#monthly').text(monthly_pay).parent().show();
    $('input[name="initPay"]').val(cache);
    $('input[name="creditAmount"]').val(total-cache);
    $('input[name="price"]').val(total);
    $('input[name="numInstalment"]').val(m);
    $('input[name="instalment"]').val(monthly_pay);
    var d = new Date();
    d.setDate(d.getDate()+20);
    var year = d.getFullYear();
    var month = (d.getMonth()+1).toString();
    if (month.length==1)
	month = "0"+month;
    var day = d.getDate().toString();
    if (day.length==1)
	day = "0"+day;
    $('input[name="annuityDate"]').val(day+'.'+month+'.'+year);
    $('input[name="annuityDay"]').val(day);
}

var uploadedFiles = {};
var deletedFiles = {};
function save(e){
    $('iframe').remove();
    var names_for_upload = JSON.stringify(_(uploadedFiles).keys());
    var i = _.template('<iframe id="credit_uploader" name="credit_uploader" src="/credit_uploader?file_names_for_upload={{_names_for_upload}}" width="1" height="1" style="position:absolute;left:-10px;" border="0"></iframe>',
    		       {_names_for_upload:encodeURIComponent(names_for_upload)});
    //
    $('body').append(i);
    var data = {};
    _($('input').toArray().concat($('select').toArray())).
	each(function(_el){
		 var el = $(_el);
		 if (el.attr('type')&&el.attr('type').toLowerCase()=='file')
		     return;
		 data[el.attr('name')] = el.val();
	     });
    $('#credit_data').val(encodeURIComponent(JSON.stringify(data)));
    $('#file_names').val(encodeURIComponent(JSON.stringify(uploadedFiles)));
    $('#order_id').val($('#orderid').text());
    $('#deleted_files').val(encodeURIComponent(JSON.stringify(deletedFiles)));
    $('#credit_submit').click();
    updateSave(1);
}
function updateSave(tries){
    var iframe = $('iframe')[0];
    if (tries == 10){
	alert('что-то пошло не так :(');
	return;
    }
    if (iframe == undefined){
	_.delay(function(){updateSave(tries*2);},tries*100);
	return;
    }
    var status;
    if (iframe.contentDocument ) {
	status = iframe.contentDocument.getElementById('status');
    } else if ( iframe.contentWindow ) {
	status = iframe.contentWindow.document.getElementById('status');
    }
    if (!status){
	_.delay(function(){updateSave(tries*2);},tries*100);
	return;
    }
    if ($(status).text()=="ok"){
	console.log(sending);
	if (!sending)
	    alert('получилось');
	else
	    sending = false;
	saved = true;
	installUploadedFiles();
    }
    else
	alert('что-то пошло не так :(');
}

function deleteFile(key){
    return function(e){
	e.preventDefault();
	var target = $(e.target);
	// if (!key)
	//     key = target.attr('id');
	var field = key;
	if (!field)
	    field = target.attr('id');
	$.ajax({
		   url:'/deleteCreditAttachment',
		   data:{'field':field,
			 'order':$('#orderid')
			 .text()},
		   success:function(data){
		       if (data=="ok"){
			   deletedFiles[field] = target.parent().text().replace(target.text(),'');
			   target.parent().remove();
		       }
		       else
			   alert('что-то пошло не так');
		   },
		   error:function(data){
		       alert('что-то пошло не так');
		   }
	       });
    };
}


function installUploadedFiles(){
    _(uploadedFiles).chain().keys().each(function(key){
					    var inp = $('input[name="'+key+'"]');
					    var file_name = _(uploadedFiles[key].split('/')).last();
					    file_name= _(file_name.split('\\')).last();
					    inp.before('<a target="_blank" href="/image/'+
						       $.cookie('pc_user')+'/'+file_name+
						       '">'+file_name+
						       '<span style="margin-left:5px;">удалить</span></a>');
					    var span = inp.prev().find('span');
					    inp.remove();
					    span.after('<br/>');
					    span.click(deleteFile(key));
					});
    uploadedFiles = {};
    deletedFiles = {};
}
var saved = false;
var sending = false;

function init(){
    $('#calc').click(recalculate);
    var tot = $('#total');
    if (tot.text()==''){
	var pa = tot.parent();
	tot.remove();
	pa.append('<input style="margin-left:40px;" id="total" name="mock_total"/>');
    }
    else{
	$('#calc').click();
    }
    var it = 0;
    function addFile(e){
	var target = $(e.target);
	var _name = target.attr('name');
	uploadedFiles[_name] = target.val();
	var letters = _name.match(/[a-zA-Z_]*/g)[0];
	var number = _name.substring(letters.length);
	if (!number)
	    number = 0;
	var new_number = parseInt(number)+1;
	target.after('<input type="file" name="'+letters+new_number+'"/>');
	target.next().change(addFile);
    }
    $('input[type="file"]').change(addFile);
    $('.save').click(save);
    $('a.uploaded_file span').click(deleteFile());
    $('input').change(function(e){saved=false;});
    $('.send').click(function(e){			 
			 if (!saved){
			     sending = true;
			     save();
			 }
			 validate();
		     });
}
function validate(){
    
}
init();