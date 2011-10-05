$(function(){
      var description = $('#model_description');
      var textarea = $(document.createElement('textarea'));
      textarea.val(description.html());
      textarea.css('width','500px');
      description.html(textarea);
      textarea.css('height','110px');
      textarea.parent().css('height','115px');
      $('.our')
	  .css('cursor','pointer')
	  .click(function(e){			  
			  var our = $(e.target);
			  if (our.attr('class')!='our')
			      return;
			  var _textarea = $(document.createElement('textarea'));
			  _textarea.val(our.html());
			  our.html(_textarea);
			  our.unbind('click');
		      });
      function store(){

	  var model_to_store = {};
	  var items = {};
	  for (_id in model){

	      var new_model_comp = filterByCatalogs(_(new_model).values(),
						    getCatalogs(model[_id]))[0];
	      var body = jgetBodyById(_id);
	      if (isMother(body)){
		  model_to_store["mother_catalogs"] = getCatalogs(new_model_comp);
	      }
	      if (isProc(body)){
		  model_to_store["proc_catalogs"] = getCatalogs(new_model_comp);
	      }
	      var to_store = null;
	      if (new_model_comp.count){
		  to_store = [];
		  for (var i=0;i<new_model_comp.count;i++){
		      to_store.push(new_model_comp['_id']);
		  }
	      }
	      else{
		  if (!new_model_comp['_id'].match('no'))
		      to_store = new_model_comp['_id'];
	      }
	      var part = jgetPart(body);
	      items[part] = to_store;
	  }
	  model_to_store['items'] = items;
	  if (uuid)
	      model_to_store['id'] = uuid;
	  model_to_store['installing'] = $('#oinstalling').is(':checked');
	  model_to_store['building'] = $('#obuild').is(':checked');
	  model_to_store['dvd'] = $('#odvd').is(':checked');
	  model_to_store['description'] = $('#model_description textarea').val();
	  var to_send = {'model':model_to_store};
	  to_send['hows'] = [];
	  var ours = $('.our');
	  for (var i = 0;i<ours.length;i++){
	      var our = $(ours.get(i));
	      var val = our.html();
	      var _textarea = our.find('textarea');
	      if (_textarea.length>0)
		  val = _textarea.val();
	      to_send['hows'].push(val);
	  }
	  to_send['_id'] = _(document.location.href.split('/')).last();
	  $.ajax({
	  	     url:'../storemodel',
	  	     data:{'to_store':JSON.stringify(to_send)},
		     type:'POST',
		     datatype: "json",
	  	     success:function(data){if (data=="ok")alert('Получилось');},
		     error:function(er){
					if (er.responseText.match('ok'))
					{
					    alert('Получилось!');
					}
					else{
					    alert('Что пошло не так! Не удается сохранить!');
					}
				    }
	  	 });
      }
      $('#tocart').unbind('click').click(store);
  });