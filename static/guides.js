var masked = false;

function makeMask(action, _closing){
    function _makeMask(e){
	//try{
            if (e)
                e.preventDefault();
            var maskHeight = $(document).height();
            var maskWidth = $(window).width();
            $('#mask').css({'width':maskWidth,'height':maskHeight})
                .fadeIn(400)
                .fadeTo("slow",0.9);
            var winH = $(window).scrollTop();
            var winW = $(window).width();

            var details = $('#details');

            var _left = winW/2-details.width()/2;
            var _top;
            if (winH == 0)
                _top = 80;
            else
                _top = winH+80;
            details.css('top', _top);
            details.css('left', _left);

            action();
	    details.prepend('<div id="closem"></div><div style="clear:both;"></div>');
	    $('#closem').click(function(e){$('#mask').click();});
            function closing(){
            }
            details.fadeIn(600, closing);
            masked = true;            
            $('#mask').click(function () {
                                 $(this).hide();
                                 details.hide();
                                 masked = false;
                                 _closing();
                             });

            $(document.documentElement).keyup(function (event) {
                                                  if (event.keyCode == '27') {
                                                      $('#mask').click();
                                                  }
                                              });
        //}
        // catch (e){
        //     console.log(e);
        // }
    }
    return _makeMask;
}



var myMessages = ['popups_info'];
function hideAllMessages()
{
    var messagesHeights = new Array(); // this array will store height for each

    for (var i=0; i<myMessages.length; i++)
    {
        messagesHeights[i] = $('.' + myMessages[i]).outerHeight(); // fill array
        $('.' + myMessages[i]).css('top', -messagesHeights[i]); //move element outside viewport
    }
}
function showMessage(type)
{
    $('.'+ type +'-trigger').click(function(e){
                                       e.preventDefault();
                                       hideAllMessages();
                                       //var winH = $(window).scrollTop();
                                       $('.'+type).animate({top:"0",left:"0"}, 500);
                                   });
}
// $(function(){hideAllMessages();

//              // Show message
//              for(var i=0;i<myMessages.length;i++)
//              {
//                  showMessage(myMessages[i]);
//              }

//              // When message is clicked, hide it
//              $('.message').click(function(){
//                                      $(this).animate({top: -$(this).outerHeight()}, 500);
//                                  });

//             });

var filled_selects_helps = {    
};

var showYa = function (_id, _link){
    new Ya.share({
                     element: _id,
                     elementStyle: {
                         'type': 'none',
                         'border': false,
                         'quickServices': ['vkontakte', 'odnoklassniki','facebook','twitter','lj','moimir','moikrug','liveinternet']
                     },
                     link:_link,
                     title: 'buildpc.ru Просто купить компьютер',
                     serviceSpecific: {
                         twitter: {
                             title: 'buildpc.ru Просто купить компьютер'
                         }
                     }
                 });
};

$(function()
  {
      hideAllMessages();
      $('#tips').click(function(e){
                           e.preventDefault();
                           guider.createGuider({
                                                   attachTo: "#7388",
                                                   description: "Список доступных компонентов. Описание компонента смотрите ниже на странице.",
                                                   id: "mother",
                                                   position: 6,
                                                   width: 160
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#7399 .body",
                                                   description: "Название выбранного компонента",
                                                   id: "body",
                                                   position: 7,
                                                   width: 100
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#7388 .cheaper",
                                                   description: "Можно менять компоненты не открывая список.",
                                                   id: "cheaperBetter",
                                                   position: 6,
                                                   width: 130
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#osoft",
                                                   description: "Некоторые опции можно отключить совсем.",
                                                   id: "options",
                                                   position: 6,
                                                   width: 130
                                               }).show();


                           guider.createGuider({
                                                   attachTo: "#gbetter",
                                                   description: "Эти кнопки позволяют изменять компоненты по алгоритму, который особое внимание уделяет производительности компьютера.",
                                                   id: "GCheaperGBetter",
                                                   position: 7,
                                                   width: 140
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#component_title",
                                                   description: "На этой вкладке описание компонента от поставщика.",
                                                   id: "descritpion",
                                                   position: 11,
                                                   width: 300
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#ourcomments",
                                                   description: "На этой вкладке наши комментарии по выбору компонента.",
                                                   id: "ourcomments",
                                                   position: 3,
                                                   width: 160
                                               }).show();

                           guider.createGuider({
                                                   attachTo: "#large_price",
                                                   description: "Текущая цена и индекс производительности",
                                                   id: "largeprice",
                                                   position: 9,
                                                   width: 160
                                               }).show();

                           $('body').click(function(e){
                                               if ($(e.target).attr('id') == 'tips')return;
                                               guider.hideAll();
                                           });
                       });

      function fillSelectHelps(action){
	  if (fillSelectHelps[current_row])
	      return action();
	  $.ajax({
                     url:'/select_helps/how_'+current_row,
		     dataType: 'json',
                     success:function(data){					    
                         var row_index;
                         var trs = $('.component_viewlet');
                         for (var i=0;i<trs.length;i++){
                             if (trs.get(i).id==current_row){
				 var our = $($('.our').get(i));
                                 our.html(data.html);
				 fillSelectHelps[current_row] = true;				 
				 if(our.parent().css('margin-left')=='0px'){
				     our.hide();
				 }
                                 break;
                             }
                         }
                         action();
                     },
                     error:function(){
			 fillSelectHelps[current_row] = true;
                         action();
                     }
                 });
      }
      
      function swapTabs(e){
          var active = $('.active');
          var target = $(e.target);
          var klass = target.attr('class');
          target.attr('class', active.attr('class'));
          active.attr('class', klass);
          target.unbind('click');
          active.click(swapTabs);

          if (target.attr('id') == 'ourcomments'){
              var container = $('#descriptions');
              container.data('jScrollPanePosition', 0);
              container.css('top','0');
              function animate(){
                  var desc = $('.description');
		  desc.find('.our').show();
		  $('#descriptions').jScrollPaneRemove();
		  $('#descriptions').jScrollPane();
		  desc.animate({'margin-left':'-=912'}, 400);
              }
	      fillSelectHelps(animate);                      
          }
          else{
	      var desc = $('.description');
	      desc.find('.our').hide();
	      desc.animate({'margin-left':'+=912'}, 400);
	  }              
      }
      $('.inactive').click(swapTabs);
      $('.body').click(function(){fillSelectHelps(function(){});});
      $('.our').hide(); 
      //$('.guider_description ul li')

  });