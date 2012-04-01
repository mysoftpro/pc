_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var faq_template = _.template('<div style="opacity:0" class="{{klass}}"><h3 class="faqtitle"></h3><div><i class="icon icon-user"></i><span class="faqauthor">{{author}}</span><span style="margin-left:5px;" class="faqdate">{{date}}</span></div><div class=\"faqtags\">{{tags}}</div><div class="faqbody well">{{body}}</div>{{links}}</div>');
var link_template = '<div class="faqlinks"><span class="btn postAnswer">комментировать</span></div>';

function makeTags(doc){
    var retval = '';
    if (doc.tags)
        retval = _(doc.tags)
        .map(function (tag){return _.template('<a href="/blog?tag={{tag}}">{{tag}}</a>',
                                       {tag:tag,url:encodeURI(tag)});})
        .join('');
    return retval;
}

function init(){
    function sendSuccess(data, to_send, target, parent){
        var d = new Date();
        var _date = d.getDate()+'.';
        _date +=+d.getMonth()+1+'.';
        _date +=+d.getFullYear()+'';
        var middle = $('#faq');
        var author = $.cookie('pc_user');
        if (to_send['name'])
            author = to_send['name'];

        var before_append = function(_html){
            middle.children().first().before(_html);
        };
        var after_append = function(){return middle.children()
                                      .first();};
        var klass = 'faqrecord';
        var links = link_template;
        if (parent){
	    links = '';
            klass = 'faqrecord fanser';
            before_append = function(_html){
                target.parent().find('.faqlinks').after(_html);
            };
            after_append = function (){
                $('#faqanswer').hide();
                var next = target
                    .parent()
                    .find('.faqlinks').next();
                return next;
            };
        }
        before_append(faq_template(
                          {'body':to_send['txt'],
                           'author':author,
                           'date':_date,
                           'links':links,
                           'klass':klass,
			   'tags':''}));
        var aa = after_append();
        aa.attr('id',data).animate({'opacity':'1.0'},500);
        if (!parent){
            aa.find('a').click(postAnswer);
        }
    }
    function send(e){
        var target = $(e.target);
        while (!target.attr('id') &&
               target.attr('id')!=='faq_top' &&
               target.attr('id')!=='faqanswer'){
            target = target.parent();
        }
        var _area,_email,_name;
        var parent;
        _area = target.find('input[name="txt"]');
        _email = target.find('input[name="email"]');
        _name = target.find('input[name="name"]');
        parent = target.parent().attr('id');

        //}
        var to_send = {txt:_area.val(),name:_name.val(),email:_email.val()};
        var path = document.location.href.split('?')[0];
        if (parent)
            to_send['parent'] =parent;
	if (path.match('blog'))
            to_send['type']='blog';
        else
            to_send['type']='faq';
        
        $.ajax({
                   url:'/storefaq',
                   data:to_send,
                   type:'post',
                   success:function(data){sendSuccess(data, to_send, target, parent);}
               });
        //}
	//zz
    };
    
    $('.sendfaq').click(send);

    var form = $('form').html();
    var answer  =$(document
                   .createElement('div'))
        .attr('id','faqanswer')
        .html(form);

    answer.css({'opacity':'0'});
    function postAnswer(e){

        var target = $(e.target);
        var pa = target.parent().parent();
        answer.animate({'opacity':'0'},400);
        answer.find('.sendfaq').unbind('click')
            .click(send);
        _.delay(function(){
                    pa.css('margin-bottom','5px').find('.faqlinks').after(answer);
                    answer.show()
                        .animate({'opacity':'1.0'},
                                 400);},500);

    }
    $('.faqlinks .postAnswer').click(postAnswer);
    function moreRecords(event, direction){
        if (direction == 'up')return;
        $.fn.waypoint('destroy');

        var last = $('.faqrecord').last();
        var id = last.attr('id');
        var key = [];
        var after = last;
        var from_answer = false;
        if (last.attr('class').match('answer')){
            key.push(last.parent().attr('id'));
            after = last;
            key.push(last.attr('id'));
            from_answer = true;
        }
        else{
            key.push(last.attr('id'));
            key.push('z');
        }
	var url = 'fromBlog?startkey='+encodeURI(JSON.stringify(key))+
                       '&limit=20&include_docs=true&descending=true';
	//tags!
        var tags = '';	
	var tagmatch = document.location.search.match(/tag=(.*)$/g);
        if (tagmatch){
	    var tag = tagmatch[0].replace('tag=','');
	    var startkey=[tag,key[0]];
	    var endkey = [tag,'0'];
	    url = 'fromBlog?startkey='+JSON.stringify(startkey)+
		'&endkey='+JSON.stringify(endkey)+
                '&limit=20&include_docs=true&descending=true&tags=t';
        }
        $.ajax({
                   url:url,
                   success:function(_data){
                       var data = eval('('+_data+')');
                       _(data['rows'])
                           .each(function(row, i){
                                     if (i==0)return;
                                     var doc = row.doc;
                                     if (row.key[1]=='z'){
                                         var au = doc['author'];
                                         if (doc['name'])
                                             au = doc['name'];
                                         after
                                             .after(faq_template(
                                                        {'body':doc['txt'],
                                                         'author':au,
                                                         'date':doc['date'],
                                                         'links':link_template,
                                                         'klass':'faqrecord',
                                                        'tags':makeTags(doc)}));
                                         after = after.next();
                                         after.find('.postAnswer').click(postAnswer);
                                         if (doc['title'])
                                             after
                                             .find('h3').text(doc['title'])
                                             .show();
                                         after.attr('id',doc['_id']);
                                         after.animate({opacity:'1.0'},300);
                                     }
                                     else{
                                         after
                                             .append(faq_template(
                                                         {'body':doc['txt'],
                                                          'author':doc['author'],
                                                          'date':doc['date'],
                                                          'links':'',
                                                          'klass':'faqrecord fanser',
                                                          'tags':makeTags(doc)}));
                                         after.children().last().animate({opacity:'1.0'},300);
                                     }
                                 });
                       var all_records = $('.faqrecord').toArray();
                       var median = $(all_records[all_records.length-8]);
                       median.waypoint(moreRecords);
                   }
               });
    }
    var all_records = $('.faqrecord').toArray();
    var median = $(all_records[all_records.length-8]);
    median.waypoint(moreRecords);
};

init();