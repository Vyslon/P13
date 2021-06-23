$(".delete").change(function() {

  $(this.form).submit(function SubForm(e) {
    e.preventDefault();
    $.ajax({
      url: '/main/deleteCompany/',
      type: 'post',
      data: $(this).serialize(),
      success: function() {}
    });
  });
  $(this.form).submit();
});
