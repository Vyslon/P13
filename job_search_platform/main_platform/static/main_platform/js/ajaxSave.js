$(".save").change(function() {
  $(this).parent().hide();
  $(this).parent().next().removeClass("is-hidden");
  
  $(this.form).submit(function SubForm(e) {
    e.preventDefault();
    $.ajax({
      url: '/main/saveCompany/',
      type: 'post',
      data: $(this).serialize(),
      success: function() {}
    });
  });
  $(this.form).submit();
});
