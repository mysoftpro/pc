var masked = false;

function makeMask(action, _closing){
    function _makeMask(e){
	try{
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

            function closing(){
            }
            details.fadeIn(600, closing);
            masked = true;
            $('#details.close').click(function (e) {
                                          e.preventDefault();
                                          $('#mask').hide();
                                          details.hide();
                                          masked = false;
                                          _closing();
                                      });
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
        }
        catch (e){
            log(e);
        }
    }
    return _makeMask;
}



var myMessages = ['popups_info','popups_warning','popups_error','popups_success'];
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
$(function(){hideAllMessages();

             // Show message
             for(var i=0;i<myMessages.length;i++)
             {
                 showMessage(myMessages[i]);
             }

             // When message is clicked, hide it
             $('.message').click(function(){
                                     $(this).animate({top: -$(this).outerHeight()}, 500);
                                 });

            });
