(function ($) {
  "use strict";

  var first_name = $(".first_name");
  var last_name = $(".last_name");
  var father_name = $(".father_name");
  var gender = $(".gender");
  var date_of_birth = $(".date_of_birth");
  var nationality = $(".nationality");
  var email = $(".email");
  var phone_number = $(".phone_number");
  var highest_qualification = $(".highest_qualification");

  var resume = $("#uplaod");

  var first_flag = true;
  var second_flag = true;
  var third_flag = true;
  var fourth_flag = true;
  //* Form js

  function verificationForm() {
    //jQuery time
    var current_fs, next_fs, previous_fs; //fieldsets
    var left, opacity, scale; //fieldset properties which we will animate
    var animating; //flag to prevent quick multi-click glitches

    $(".do-submit").click(function () {

      var education_generalized1 = [];
      var education_generalized2 = [];
      var education_generalized3 = [];
      var education_generalized4 = [];
      var education_generalized5 = [];

      var experience_generalized1 = [];
      var experience_generalized2 = [];
      var experience_generalized3 = [];
      var experience_generalized4 = [];
      var experience_generalized5 = [];
      // Layer 8
      //             $(".do-submit").attr('disabled', 'disabled');
      $("#academic_desc_table tr").each(function (e) {
        education_generalized1.push($(this).find("td:eq(0)").text());
        education_generalized2.push($(this).find("td:eq(1)").text());
        education_generalized3.push($(this).find("td:eq(2)").text());
        education_generalized4.push($(this).find("td:eq(3)").text());
        education_generalized5.push($(this).find("td:eq(4)").text());
      });
      $("#experience_desc_table tr").each(function (e) {
        if (
          $(this).find("td:eq(2)").text()
        ) {
          experience_generalized1.push($(this).find("td:eq(0)").text());
          experience_generalized2.push($(this).find("td:eq(1)").text());
          experience_generalized3.push($(this).find("td:eq(2)").text());
          experience_generalized4.push($(this).find("td:eq(3)").text());
          experience_generalized5.push($(this).find("td:eq(4)").text());
        }
      });
      $(".education_generalized1").val(education_generalized1);
      $(".education_generalized2").val(education_generalized2);
      $(".education_generalized3").val(education_generalized3);
      $(".education_generalized4").val(education_generalized4);
      $(".education_generalized5").val(education_generalized5);
      $(".experience_generalized1").val(experience_generalized1);
      $(".experience_generalized2").val(experience_generalized2);
      $(".experience_generalized3").val(experience_generalized3);
      $(".experience_generalized4").val(experience_generalized4);
      $(".experience_generalized5").val(experience_generalized5);
    });

    $("#confirm_policy").on('change', function(e) {
        if ($("#confirm_policy").prop('checked') == true){
          $(".fourth-button").prop("disabled", false)
        }else{
          $(".fourth-button").prop("disabled", true)
        }
    });

    $("#academic_desc_table").on("click", ".btn-edit-edu-info", function (e) {
      e.stopPropagation();
      e.preventDefault();
      var target = $(this).parents("#myModalAcademic");
      target.find("input[name='operation_type']").val("add");
      $("#myModalAcademic")
        .find("input[name='start_year']")
        .val($.trim($(this).closest("tr").find("td:eq(0)").text()));
      $("#myModalAcademic")
        .find("input[name='completion_year']")
        .val($.trim($(this).closest("tr").find("td:eq(1)").text()));
      $("#myModalAcademic")
        .find("input[name='degree']")
        .val($.trim($(this).closest("tr").find("td:eq(2)").text()));
      $("#myModalAcademic")
        .find("input[name='specialization']")
        .val($.trim($(this).closest("tr").find("td:eq(3)").text()));
      $("#myModalAcademic")
        .find("input[name='university']")
        .val($.trim($(this).closest("tr").find("td:eq(4)").text()));
      $("#myModalAcademic").find("input[name='operation_type']").val("update");
      $("#myModalAcademic")
        .find("input[name='opr_id']")
        .val($.trim($(this).closest("tr").index()));
      $("#myModalAcademic").modal();
    });
    $("#experience_desc_table").on("click", ".btn-edit-exp-info", function (e) {
      e.stopPropagation();
      e.preventDefault();
      var target = $(this).parents("#myModalExperience");
      target.find("input[name='operation_type']").val("add");
      $("#myModalExperience")
        .find("input[name='job_title']")
        .val($.trim($(this).closest("tr").find("td:eq(0)").text()));
      $("#myModalExperience")
        .find("input[name='company']")
        .val($.trim($(this).closest("tr").find("td:eq(1)").text()));
      $("#myModalExperience")
        .find("input[name='start_date']")
        .val($.trim($(this).closest("tr").find("td:eq(2)").text()));
      $("#myModalExperience")
        .find("input[name='end_date']")
        .val($.trim($(this).closest("tr").find("td:eq(3)").text()));
      if ($.trim($(this).closest("tr").find("td:eq(4)").text()) == 't') {
        $("#myModalExperience").find("input[name='is_current']").prop('checked', true)
      } else {
        $("#myModalExperience").find("input[name='is_current']").prop('checked', false)
      }
      $("#myModalExperience")
        .find("input[name='operation_type']")
        .val("update");
      $("#myModalExperience")
        .find("input[name='opr_id']")
        .val($.trim($(this).closest("tr").index()));
      if ($("#myModalExperience").find("input[name='is_current']").prop('checked') == true) {
        $("#myModalExperience")
        .find("input[name='end_date']").parent().hide()
      }else {
        $("#myModalExperience")
        .find("input[name='end_date']").parent().show()
      }
      $("#myModalExperience").modal();
    });
    $("#academic_desc_table").on("click", ".btn-delete-edu-info", function (e) {
      $(this).closest("tr").remove();
    });
    $("#experience_desc_table").on(
      "click",
      ".btn-delete-exp-info",
      function (e) {
        $(this).closest("tr").remove();
      }
    );
    $(".submit-job-definition").click(function () {
      var today_date = new Date();
      var selected_date = new Date($(".post_job_picker").val());

      if (today_date.getFullYear() > selected_date.getFullYear()) {
        alert("Please enter proper closing date");
        $(".post_job_picker").val("");
        return false;
      }
      if (!parseInt(selected_date.getMonth())) {
        alert("Please enter proper closing date");
        $(".post_job_picker").val("");
        return false;
      }
      if (!parseInt(selected_date.getDate())) {
        alert("Please enter proper closing date");
        $(".post_job_picker").val("");
        return false;
      }
      if (!parseInt(selected_date.getFullYear())) {
        alert("Please enter proper closing date");
        $(".post_job_picker").val("");
        return false;
      }
      if (today_date > selected_date) {
        alert("Please enter proper closing date");
        $(".post_job_picker").val("");
        return false;
      } else {
      }
    });

    $(document).on("click", "#CertificationEditModal", function (e) {
      e.stopPropagation();
      e.preventDefault();
      var id = $(this).data("certification_id");
      var start_date_val = $(this)
        .parents("tr")
        .find(".certification_start_date")
        .text();
      var end_date_val = $(this)
        .parents("tr")
        .find(".certification_end_date")
        .text();
      $("#CertificationEditModal" + id).modal();
      $("#CertificationEditModal" + id)
        .find("input[name='start_date']")
        .val(start_date_val);
      $("#CertificationEditModal" + id)
        .find("input[name='end_date']")
        .val(end_date_val);
    });

    $("#top_menu li").addClass("job_portal_menus");
    $(".job_portal_menus").each(function () {
      if ($.trim($(this).text()) == "Post Job") {
        $(this).attr("groups", "base.group_erp_manager");
      }
    });
    $(document).on("click", ".certification_btn", function (e) {
      e.stopPropagation();
      e.preventDefault();
      $("#myModalCertification").modal();
      $("#myModalCertification")
        .find("input[name='operation_type']")
        .val("insert");
      $("#myModalCertification").find("input").val("");
    });
    $(".new_academic").click(function (e) {
      e.stopPropagation();
      e.preventDefault();
      var target = $(this).parents("#myModalAcademic");
      target.find("input[name='operation_type']").val("add");
      $("#myModalAcademic").modal();
      $("#myModalAcademic").find("input[name='operation_type']").val("insert");
      $("#myModalAcademic").find("input").val("");
    });

    /* affix the navbar after scroll below header */
    // Click event For Adding Academic of Applicants
    // Validation on the models can/should be improved later on

    // For Industry Practices Static Page JS
    $("div.bhoechie-tab-menu>div.list-group>a").click(function (e) {
      e.stopPropagation();
      e.preventDefault();
      $(this).siblings("a.active").removeClass("active");
      $(this).addClass("active");
      var index = $(this).index();
      $("div.bhoechie-tab>div.bhoechie-tab-content").removeClass("active");
      $("div.bhoechie-tab>div.bhoechie-tab-content")
        .eq(index)
        .addClass("active");
    });

    $(document).on("click", ".academic_btn", function (e) {
      e.stopPropagation();
      e.preventDefault();
      $("#myModalAcademic").modal();
      $("#myModalAcademic").find("input[name='operation_type']").val("insert");
      $("#myModalAcademic").find("input").val("");
    });

    $(document).on("click", ".experience_btn", function (e) {
      e.stopPropagation();
      e.preventDefault();
      $("#myModalExperience").modal();
      $("#myModalExperience")
        .find("input[name='operation_type']")
        .val("insert");
      $("#myModalExperience").find("input").val("");
      $("#myModalExperience").find("input[name='end_date']").parent().show()
      $("#myModalExperience").find("#is_current").prop('checked', false);
    });

    $("#is_current").on("change", function(e) {
      $("#myModalExperience").find(".end_date_exp").val("")
      if ($("#is_current").prop('checked') == true) {
        $("#myModalExperience").find(".end_date_exp_star").text("")
      }else {
        $("#myModalExperience").find(".end_date_exp_star").text("*")
      }
      $("#myModalExperience").find(".end_date_exp").parent().toggle()
    });

    $(document).on("click", "#add_academic", function (e) {
      var target = $(this).parents("#myModalAcademic");
      var validation_flag = true;

      if (
        $.trim(target.find("input[name='operation_type']").val()) == "update"
      ) {
        if (
          $(".start_year_edu").val() == "" ||
          $(".completion_year_edu").val() == "" ||
          $(".degree_edu").val() == "" ||
          $(".university_edu").val() == ""
        ) {
          alert("Please fill all the fields");
          return false;
        } else {
          var st_edu = new Date($(".start_year_edu").val());
          var end_edu = new Date($(".completion_year_edu").val());
          var st_year = st_edu.getFullYear();
          var end_year = end_edu.getFullYear();
          if (st_year < 1950 || end_year < 1950) {
            alert(
              "Please enter the date in the greogrian calendar format. You cannot enter a date prior to the year 1950"
            );
            return false;
          } else {
            $(
              "#academic_desc_table tr:eq(" +
                $.trim(target.find("input[name='opr_id']").val()) +
                ")"
            ).replaceWith(
              "<tr><td>" +
                $.trim(target.find("input[name='start_year']").val()) +
                "</td><input type='hidden' name='hidden1' value=" +
                $.trim(target.find("input[name='start_year']").val()) +
                "/><td>" +
                $.trim(target.find("input[name='completion_year']").val()) +
                "<input type='hidden' name='hidden2' value=" +
                $.trim(target.find("input[name='completion_year']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='degree']").val()) +
                "<input type='hidden' name='hidden3' value=" +
                $.trim(target.find("input[name='degree']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='specialization']").val()) +
                "<input type='hidden' name='hidden4' value=" +
                $.trim(target.find("input[name='specialization']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='university']").val()) +
                "<input type='hidden' name='hidden5' value=" +
                $.trim(target.find("input[name='university']").val()) +
                "/></td><td><button type=button class='btn btn-edit-edu-info'><i class='fa fa-pencil-square-o'></i></button><button class='btn btn-delete-edu-info'><i class='fa fa-trash'></i></button></td></tr>"
            );
          }
        }
      } else {
        if (
          $(".start_year_edu").val() == "" ||
          $(".completion_year_edu").val() == "" ||
          $(".degree_edu").val() == ""  ||
          $(".university_edu").val() == ""
        ) {
          alert("Please fill all the fields");
          return false;
        } else {
          var st_edu = new Date($(".start_year_edu").val());
          var end_edu = new Date($(".completion_year_edu").val());
          var st_year = st_edu.getFullYear();
          var end_year = end_edu.getFullYear();
          if (st_year < 1950 || end_year < 1950) {
            alert(
              "Please enter the date in the greogrian calendar format. You cannot enter a date prior to the year 1950"
            );
            return false;
          } else {
            $("#academic_desc_table tr:last").after(
              "<tr style='color:black; font-size:13px;'><td>" +
                $.trim(target.find("input[name='start_year']").val()) +
                "</td><input type='hidden' name='hidden1' value=" +
                $.trim(target.find("input[name='start_year']").val()) +
                "/><td>" +
                $.trim(target.find("input[name='completion_year']").val()) +
                "<input type='hidden' name='hidden2' value=" +
                $.trim(target.find("input[name='completion_year']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='degree']").val()) +
                "<input type='hidden' name='hidden3' value=" +
                $.trim(target.find("select[name='degree']").val()) +
                "></td><td>" +
                $.trim(target.find("input[name='specialization']").val()) +
                "<input type='hidden' name='hidden4' value=" +
                $.trim(target.find("input[name='specialization']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='university']").val()) +
                "<input type='hidden' name='hidden5' value=" +
                $.trim(target.find("select[name='university']").val()) +
                "/></td><td><button type=button class='btn btn-edit-edu-info'><i class='fa fa-pencil-square-o'></i></button><button class='btn btn-delete-edu-info'><i class='fa fa-trash'></i></button></td></tr>"
            );
            $("#myModalAcademic")
              .find("input[name='operation_type']")
              .val("add");
          }
        }
      }
      $("#myModalAcademic").modal("hide");
    });

    $(document).on("click", "#add_experience", function (e) {
      var target = $(this).parents("#myModalExperience");

      if (
        $.trim(target.find("input[name='operation_type']").val()) == "update"
      ) {
        if (
          $(".job_title_exp").val() == "" ||
          $(".company_exp").val() == "" ||
          $(".start_date_exp").val() == "" ||
          ($(".end_date_exp").val() == ""  && $("#is_current").prop('checked') == false )
        ) {
          alert("Please fill all the fields");
          return false;
        } else {
          var st_exp = new Date($(".start_date_exp").val());
          var end_exp = new Date($(".end_date_exp").val());
          var st_year = st_exp.getFullYear();
          var end_year = end_exp.getFullYear();
          if (st_year < 1950 || end_year < 1950) {
            alert(
              "Please enter the date in the greogrian calendar format. You cannot enter a date prior to the year 1950"
            );
            return false;
          } else {
            $(
              "#experience_desc_table tr:eq(" +
                $.trim(target.find("input[name='opr_id']").val()) +
                ")"
            ).replaceWith(
              "<tr><td>" +
                $.trim(target.find("input[name='job_title']").val()) +
                "</td><input type='hidden' name='hidden1' value=" +
                $.trim(target.find("input[name='job_title']").val()) +
                "/><td>" +
                $.trim(target.find("input[name='company']").val()) +
                "<input type='hidden' name='hidden2' value=" +
                $.trim(target.find("input[name='company']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='start_date']").val()) +
                "<input type='hidden' name='hidden3' value=" +
                $.trim(target.find("input[name='start_date']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='end_date']").val()) +
                "<input type='hidden' name='hidden4' value=" +
                $.trim(target.find("input[name='end_date']").val()) +
                "/></td><td style='display:none'>" +
                $.trim(target.find("input[name='is_current']").prop('checked') == true ? 't' : '') +
                "<input type='hidden' name='hidden5' value=" +
                $.trim(target.find("input[name='is_current']").prop('checked') == true ? 't' : '') +
                "/></td><td><button type=button class='btn btn btn-edit-exp-info'><i class='fa fa-pencil-square-o'></i></button><button class='btn btn-delete-exp-info'><i class='fa fa-trash'></i></button></td></tr>"
            );
          }
        }
      } else {
        if (
          $(".job_title_exp").val() == "" ||
          $(".company_exp").val() == "" ||
          $(".start_date_exp").val() == "" ||
          ($(".end_date_exp").val() == "" && $("#is_current").prop('checked') == false )
        ) {
          alert("Please fill all the fields");
          return false;
        } else {
          var st_exp = new Date($(".start_date_exp").val());
          var end_exp = new Date($(".end_date_exp").val());
          var st_year = st_exp.getFullYear();
          var end_year = end_exp.getFullYear();
          if (st_year < 1950 || end_year < 1950) {
            alert(
              "Please enter the date in the greogrian calendar format. You cannot enter a date prior to the year 1950"
            );
            return false;
          } else {
            $("#experience_desc_table tr:last").after(
              "<tr style='color:black; font-size:13px;'><td>" +
                $.trim(target.find("input[name='job_title']").val()) +
                "</td><input type='hidden' name='hidden1' value=" +
                $.trim(target.find("input[name='job_title']").val()) +
                "/><td>" +
                $.trim(target.find("input[name='company']").val()) +
                "<input type='hidden' name='hidden2' value=" +
                $.trim(target.find("input[name='company']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='start_date']").val()) +
                "<input type='hidden' name='hidden3' value=" +
                $.trim(target.find("input[name='start_date']").val()) +
                "/></td><td>" +
                $.trim(target.find("input[name='end_date']").val()) +
                "<input type='hidden' name='hidden4' value=" +
                $.trim(target.find("input[name='end_date']").val()) +
                "/></td><td style='display:none'>" +
                $.trim(target.find("input[name='is_current']").prop('checked') == true ? 't' : '') +
                "<input type='hidden' name='hidden5' value=" +
                $.trim(target.find("input[name='is_current']").prop('checked') == true ? 't' : '') +
                "></td><td><button type=button class='btn btn btn-edit-exp-info'><i class='fa fa-pencil-square-o'></i></button><button class='btn btn-delete-exp-info'><i class='fa fa-trash'></i></button></td></tr>"
            );
            $("#myModalExperience")
              .find("input[name='operation_type']")
              .val("add");
          }
        }
      }
      $("#myModalExperience").modal("hide");
    });

    function isValidAge(DOB) {
      var today = new Date();
      var birthDate = new Date(DOB);
      var age = today.getFullYear() - birthDate.getFullYear();
      var m = today.getMonth() - birthDate.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      if (age >= 18) {
        return true;
      } else {
        alert("Age Should be min 18 years old.");
        return false;
      }
    }

    $(".first-button").click(function () {
      first_flag = true;
      let email_validation = /\S+@\S+\.\S+/;
      let valid_birthday = isValidAge(date_of_birth.val());
      if (!first_name.val()) {
        $(".first_name").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".first_name").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!last_name.val()) {
        $(".last_name").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".last_name").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!father_name.val()) {
        $(".father_name").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".father_name").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!gender.val() | (gender.val() == "none")) {
        $(".gender").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".gender").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!date_of_birth.val() | !valid_birthday) {
        $(".date_of_birth").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".date_of_birth").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!nationality.val() | (nationality.val() == "none")) {
        $(".nationality").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".nationality").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (!email.val()) {
        $(".email").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".email").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (email.val()) {
        if (!email_validation.test(email.val())) {
          alert("Invalide Email Address.");
          $(".email").css("border", "1px solid #cc0033");
          first_flag = false;
        } else {
          $(".email").css("border", "1px solid rgb(92 184 92 / 66%)");
        }
      }
      if (!phone_number.val()) {
        $(".phone_number").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".phone_number").css("border", "1px solid rgb(92 184 92 / 66%)");
      }
      if (
        !highest_qualification.val() |
        (highest_qualification.val() == "none")
      ) {
        $(".highest_qualification").css("border", "1px solid #cc0033");
        first_flag = false;
      } else {
        $(".highest_qualification").css(
          "border",
          "1px solid rgb(92 184 92 / 66%)"
        );
      }
      if (first_flag) {
        if (animating) return false;
        animating = true;

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //activate next step on progressbar using the index of next_fs
        $("#progressbar li")
          .eq($("fieldset").index(next_fs))
          .addClass("active");

        //show the next fieldset

        next_fs.show();
        current_fs.animate(
          {
            opacity: 0,
          },
          {
            step: function (now, mx) {
              //as the opacity of current_fs reduces to 0 - stored in "now"
              //1. scale current_fs down to 80%
              scale = 1 - (1 - now) * 0.2;
              //2. bring next_fs from the right(50%)
              left = now * 50 + "%";
              //3. increase opacity of next_fs to 1 as it moves in
              opacity = 1 - now;
              current_fs.css({
                position: "absolute",
              });
              next_fs.css({
                left: left,
                opacity: opacity,
              });
            },
            duration: 800,
            complete: function () {
              current_fs.hide();
              animating = false;
            },
            //this comes from the custom easing plugin
            easing: "easeInOutBack",
          }
        );
      }
    });

    $(".second-button").click(function () {
      second_flag = true;
      if (second_flag) {
        if (animating) return false;
        animating = true;

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //activate next step on progressbar using the index of next_fs
        $("#progressbar li")
          .eq($("fieldset").index(next_fs))
          .addClass("active");

        //show the next fieldset

        next_fs.show();
        current_fs.animate(
          {
            opacity: 0,
          },
          {
            step: function (now, mx) {
              //as the opacity of current_fs reduces to 0 - stored in "now"
              //1. scale current_fs down to 80%
              scale = 1 - (1 - now) * 0.2;
              //2. bring next_fs from the right(50%)
              left = now * 50 + "%";
              //3. increase opacity of next_fs to 1 as it moves in
              opacity = 1 - now;
              current_fs.css({
                position: "absolute",
              });
              next_fs.css({
                left: left,
                opacity: opacity,
              });
            },
            duration: 800,
            complete: function () {
              current_fs.hide();
              animating = false;
            },
            //this comes from the custom easing plugin
            easing: "easeInOutBack",
          }
        );
      }
    });

    $(".third-button").click(function () {
      third_flag = true;
      if (third_flag) {
        if (animating) return false;
        animating = true;
        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //activate next step on progressbar using the index of next_fs
        $("#progressbar li")
          .eq($("fieldset").index(next_fs))
          .addClass("active");

        //show the next fieldset

        next_fs.show();
        current_fs.animate(
          {
            opacity: 0,
          },
          {
            step: function (now, mx) {
              //as the opacity of current_fs reduces to 0 - stored in "now"
              //1. scale current_fs down to 80%
              scale = 1 - (1 - now) * 0.2;
              //2. bring next_fs from the right(50%)
              left = now * 50 + "%";
              //3. increase opacity of next_fs to 1 as it moves in
              opacity = 1 - now;
              current_fs.css({
                position: "absolute",
              });
              next_fs.css({
                left: left,
                opacity: opacity,
              });
            },
            duration: 800,
            complete: function () {
              current_fs.hide();
              animating = false;
            },
            //this comes from the custom easing plugin
            easing: "easeInOutBack",
          }
        );
      }
    });

    $('#toggle_privacy').on('click', function(e) {
      e.preventDefault()
      $("#privacy_part").toggle()
    });

    $(".fourth-button").click(function (e) {
      fourth_flag = true;

      if (!document.getElementById("upload").files[0]) {
        $("#upload").css({
          background: "#e15f5f",
          color: "white",
          "border-color": "#e15f5f",
        });
        fourth_flag = false;
        alert("Please Upload a file");
      } else {
        $("#upload").css({
          background: "#5cb85c",
          color: "white",
          "border-color": "#5cb85c",
        });
      }
      if ($("#confirm_policy").prop('checked') == false){
        alert("You need to check the applicant declartion first.")
        e.preventDefault()
        fourth_flag = false
      }
      if (fourth_flag) {
        if (animating) return false;
        animating = true;

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //activate next step on progressbar using the index of next_fs
        $("#progressbar li")
          .eq($("fieldset").index(next_fs))
          .addClass("active");

        //show the next fieldset

        next_fs.show();
        current_fs.animate(
          {
            opacity: 0,
          },
          {
            step: function (now, mx) {
              //as the opacity of current_fs reduces to 0 - stored in "now"
              //1. scale current_fs down to 80%
              scale = 1 - (1 - now) * 0.2;
              //2. bring next_fs from the right(50%)
              left = now * 50 + "%";
              //3. increase opacity of next_fs to 1 as it moves in
              opacity = 1 - now;
              current_fs.css({
                position: "absolute",
              });
              next_fs.css({
                left: left,
                opacity: opacity,
              });
            },
            duration: 800,
            complete: function () {
              current_fs.hide();
              animating = false;
            },
            //this comes from the custom easing plugin
            easing: "easeInOutBack",
          }
        );
      } else {
        e.preventDefault();
      }
    });

    $(".previous").click(function () {
      if (animating) return false;
      animating = true;

      current_fs = $(this).parent();
      previous_fs = $(this).parent().prev();

      //de-activate current step on progressbar
      $("#progressbar li")
        .eq($("fieldset").index(current_fs))
        .removeClass("active");

      //show the previous fieldset
      previous_fs.show();
      //hide the current fieldset with style
      current_fs.animate(
        {
          opacity: 0,
        },
        {
          step: function (now, mx) {
            //as the opacity of current_fs reduces to 0 - stored in "now"
            //1. scale previous_fs from 80% to 100%
            scale = 0.8 + (1 - now) * 0.2;
            //2. take current_fs to the right(50%) - from 0%
            left = (1 - now) * 50 + "%";
            //3. increase opacity of previous_fs to 1 as it moves in
            opacity = 1 - now;
            current_fs.css({
              left: left,
            });
            previous_fs.css({
              opacity: opacity,
            });
          },
          duration: 800,
          complete: function () {
            current_fs.hide();
            animating = false;
          },
          //this comes from the custom easing plugin
          easing: "easeInOutBack",
        }
      );
    });
  }

  /*Function Calls*/
  verificationForm();
})(jQuery);
