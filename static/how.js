head.ready(function(){
      guider.createGuider({
                              attachTo: "#howguider",
                              description: "Список компонентов этой модели с ценами. <br/>Чтобы прочитать описания компонента, нужно кликнуть его название.<br/> Внизу - <span style=\"float:none;margin:0;\" class=\"guiderdiv\">кнопки</span>, которыми можно подвигать окошко.",
                              id: "howguider",
                              position: 3,
                              width: 500
                          }).show();
      $('#hselect').chosen();
      $('.modellink').attr('target','_blank');
      $('.incram').click(function(e){
			     
			     var r = $('.ramcount');
			     var t = r.text();
			     r.text(parseInt(t.split(' ')[0])+1+" шт.");
			 });
      $('.decram').click(function(e){			     
			     var r = $('.ramcount');
			     var t = r.text();
			     r.text(parseInt(t.split(' ')[0])-1+" шт.");
			 });
      
  });