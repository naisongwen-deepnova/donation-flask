$(document).ready(function() {
    //alert('here')
    // 页面刚开始隐藏搜索结果的部分
    $("#resultSection").hide();

    // id为searchDonation的按钮按下触发searchDonation()方法
    $("#searchDonation").click(function() {
        keyword = $("#keyword").val();
        searchDonation(keyword);
    });

    // id为keyword的输入框内容改变触发getSuggest()方法
    $("#keyword").on("input propertychange", function() {
        getSuggest();
    });
});


// 按下联想的词就直接搜索
$(document).on("click", ".list-group-item-action", function() {
    searchDonation($(this).text());
    $("#keyword").val($(this).text());
});

// 在按下enter键的时候就搜索
$(document).keyup(function(event) {
    if (event.keyCode == 13) {
        searchDonation($("#keyword").val());
    }
});

function searchDonation(key) {
    // 首先清空result中的内容以便内容填入
    $("#result").empty();
    $.getJSON({
        url: "/donation/search?key=" + key,
        success: function(result) {
            // 获取返回的数据中我们需要的部分
            res = result.items;
            console.log(res)
            
           // 利用for插入每一个结果
            if (res.length) {
                for (i = 0; i < res.length; i++) {
                    // 将返回的结果包装成HTML
                    resultItem =
                        `
                        <div class='col-md-12 mb-4'>
                            <div class='card mb-12 shadow-sm'>
                                <div class='card-body'>
                                    <p class='text-muted' style='margin-bottom: 0.5em'>捐款人姓名：` + res[i].name + `</p>
                                    <p class='card-text'>捐款金额：` + res[i].amount + `元，备注：`+res[i].remark+`</p>
                                    <p class='card-text'><a href='/donation/certificate?id=`+ res[i].id + `' target='_blank'>查看证书</a></p>
                                </div>
                            </div>
                        </div>
                    `;
                    // 插入HTML到result中
                    $("#result").append(resultItem);
                }
                // 搜索完以后让搜索框移上去，带有动画效果
                $("section.jumbotron").animate({
                    margin: "0"
                });
                // 显示搜索结果的部分
                $("#resultSection").show();
                // 清空输入联想
                $("#suggestList").empty();
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            console.info(textStatus)
        }
    });
}

function getSuggest() {
    // 首先清空suggestList中原来的内容以便内容填入
    $("#suggestList").empty();
    // 向服务器请求联想词
    $.getJSON({
        url: "/donation/suggest?key=" + $("#keyword").val(),
        success: function(result) {
            // 获取返回的数据中我们需要的部分
            res = result;
            console.log(res)
            if (res.suggestions.length) {
                // 利用for插入每一个结果
                for (i = 0; i < res.suggestions.length; i++) {
                    // 将返回的结果包装成HTML
                    suggestItem =
                        "<a class='list-group-item list-group-item-action'>" + res.suggestions[i] + "</a>";
                    // 插入HTML到suggestList中
                    $("#suggestList").append(suggestItem);
                }
            }
        }
    });
}
