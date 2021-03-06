function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function login() {
    $('#login-password-input').removeClass('has-error');
    $('#login-username-input').removeClass('has-error');
    $('#login-message').text('');
    let link = '/login/';
    fetch(link, {
        method: 'POST',
        body: new FormData(document.getElementById('login-form')),
        // body: new FormData($('#login-form')),
        credentials: 'include',
    }).then(response => response.json()
    ).then(data => {
        if (data.ok) {
            location.reload()
        } else {
            $('#login-password-input').addClass('has-error');
            $('#login-username-input').addClass('has-error');
            $('#login-message').text(data.message);
        }
    });
}

function register() {
    for (let i = 1; i <= 5; i++) {
        $('#register-input-' + i).removeClass('has-error');
        $('#register-message-' + i).text('');
    }
    let link = '/register/';
    fetch(link, {
        method: 'POST',
        body: new FormData(document.getElementById('register-form')),
        credentials: 'include',
    }).then(response => response.json()
    ).then(data => {
        if (data.ok) {
            location.reload();
        } else {
            if (data.errors.username) {
                $('#register-input-1').addClass('has-error');
                $('#register-message-1').text(data.errors.username[0]);
            }
            if (data.errors.email) {
                $('#register-input-2').addClass('has-error');
                $('#register-message-2').text(data.errors.email[0]);
            }
            if (data.errors.nickname) {
                $('#register-input-3').addClass('has-error');
                $('#register-message-3').text(data.errors.nick_name[0]);
            }
            if (data.errors.password1) {
                $('#register-input-4').addClass('has-error');
                $('#register-message-4').text(data.errors.password1[0]);
            }
            if (data.errors.password2) {
                $('#register-input-5').addClass('has-error');
                $('#register-message-5').text(data.errors.password2[0]);
            }
        }
    });
}

function voteUp(x, id) {
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    let link = '/answervoteup/' + id;
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().next().show().html('<i class="icon icon-caret-up"></i> ' + data.count);
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));
}

function voteDown(x, id) {
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    let link = '/answervotedown/' + id;
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().prev().show().html('<i class="icon icon-caret-up"></i> ' + data.count);
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));
}

function collect(x, id) {
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    let link = '/answercollect/' + id;
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().next().show();
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));
}

function uncollect(x, id) {
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    let link = '/answeruncollect/' + id;
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().prev().show();
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));
}

function followAsk(x, id) {
    let link = '/questionfollow/' + id;
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().next().show();
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));
}

function unfollowAsk(x, id) {
    let link = '/questionunfollow/' + id;
    let headers = new Headers();
    headers.append('X-CSRFToken', getCookie('csrftoken'));
    fetch(link, {
        headers: headers,
        method: 'POST',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(response)
        }
    }).then(data => {
        if (!data.r) {
            $(x).hide().prev().show();
        } else {
            alert('error！')
        }
    }).catch(e => console.log(e));

}

function readmore(x, id) {
    let link = '/answercontent/' + id;
    fetch(link, {
        method: 'GET',
        credentials: 'include'
    }).then(response => response.json()
    ).then(data => {
        if (!data.r) {
            $(x).siblings('span').hide();
            $(x).parent().html(data.content).append('<div class="answer-time">编辑于' + data.created_date + '</p>');
        } else {
            alert('error!')
        }
    });
}

function reply(x, answer_id, comment_id) {
    let replyEeditor = $('#replyEditor-' + answer_id);
    $('.reply-btn').show();
    $(x).hide().before(replyEeditor);
    replyEeditor.show().find("input[name='reply_id']").val(comment_id);
}

function cancelReply(x) {
    $(x).parent().hide();
    $('.reply-btn').show();
}

function showComments(x, id) {


    $('#commentList-' + id).show();
    $(x).hide().next().show();
    $('#comments-' + id).append('<i class="icon icon-spin icon-spinner-snake"></i> 加载中...');
    let link = `/commentslist/${id}`;
    fetch(link, {
        method: 'GET',
        credentials: 'include'
    }).then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error('404!')
        }
    }).then(data => {
        $('#comments-' + id).empty();
        $('#comments-' + id).append(data);
    }).catch(e => console.log(e));

}

function hideComments(x, id) {
    $('#commentList-' + id).hide();
    $(x).hide().prev().show();
    $('#comments-' + id).empty();
}

function enter(x) {
    $(x).text('取消关注');
}

function leave(x) {
    $(x).text('  已关注');
}



$(function () {

    $('#messages').click(function (event) {
        $('#messagecount').html('');
        // $.get('/mark/', function(data){
        //
        // });
        // $.get('/messagelist/', {messageType: "common"}, function (data) {
        //     $('#commonMessage').html(data);
        // });

         $.get('/msglist/', {messageType: "user"}, function (data) {
            $('#msg_content').html(data);
        });
    });

    $('#thanksMessageTab').click(function (event) {
        $.get('/messagelist/', {messageType: "thanks"}, function (data) {
            // console.log(data);
            $('#thanksMessage').html(data);
        });
    });
    $('#userMessageTab').click(function (event) {
        $.get('/messagelist/', {messageType: "user"}, function (data) {
            $('#msg_content').html(data);
        });
    });
    $('#commonMessageTab').click(function (event) {
        $.get('/messagelist/', {messageType: "common"}, function (data) {
            $('#commonMessage').html(data);
        });
    });


})