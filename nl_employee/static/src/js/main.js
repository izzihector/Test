(function($) {

  $('#reset').on('click', function(){
      $('#register-form').reset();
  });

  $("input:checkbox").click(function(){
    var group = "input:checkbox[name='"+$(this).attr("name")+"']";
    $(group).attr("checked",false);
    $(this).attr("checked",true);
    alert("asdkfjasdlkf")
});

})(jQuery);