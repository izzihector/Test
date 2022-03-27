$(window).on("load", function () {
  var disabledDates = [];
  $.ajax({
    url: "/employee/leave/dates",
    success: function (msg) {
      disabledDates = msg;

      //change disabledDates to object.
      dates = JSON.parse(disabledDates);
      disabledDates = dates.disabledDates;
      console.log(disabledDates);
      $("#attachment_div").hide();
      $("#attachment_div").attr("required", false);

      var calendar = $(".calendar").pignoseCalendar({
        multiple: true,
        week: 0,
        initialize: false,

        disabledWeekdays: [6, 5],
        disabledDates: disabledDates,

        select: function (date, context) {
          /**
           * @params this Element
           * @params date moment[]
           * @params context PignoseCalendarContext
           * @returns void
           */
          // This is selected button Element.
          var $this = $(this);

          // You can get target element in `context` variable, This element is same `$(this)`.
          var $element = context.element;

          // You can also get calendar element, It is calendar view DOM.
          var $calendar = context.calendar;

          // Selected dates (start date, end date) is passed at first parameter, And this parameters are moment type.
          // If you unselected date, It will be `null`.
          if (date[0]) {
            from = $('input[name="from_date"]').val(
              moment(date[0]).format("YYYY-MM-DD")
            );
          } else {
            from = $('input[name="from_date"]').val("From");
          }
          if (date[1]) {
            to = $('input[name="to_date"]').val(
              moment(date[1]).format("YYYY-MM-DD")
            );
          } else {
            to = $('input[name="to_date"]').val("To");
          }

          console.log($('[name="leave_type"]:checked').val(), "blablab");

          if ($('[name="leave_type"]:checked').attr("attachment") == "True") {
            //function that returns the total number of days between from_date and to_date
            function get_total_days(from_date, to_date) {
              var from_date = new Date(from_date);
              var to_date = new Date(to_date);
              var total_days = 0;
              while (from_date <= to_date) {
                total_days++;
                from_date.setDate(from_date.getDate() + 1);
              }
              return total_days;
            }

            total_days = get_total_days(
              $('input[name="from_date"]').val(),
              $('input[name="to_date"]').val()
            );
            console.log(total_days, "total-days");
            console.log(
              $('[name="leave_type"]:checked').attr("max_days"),
              "max-days"
            );

            if (
              total_days >= $('[name="leave_type"]:checked').attr("max_days")
            ) {
              $("#attachment_div").show();
              $("#attachment").attr("required", true);
            } else {
              $("#attachment_div").hide();
              $("#attachment").attr("required", false);
            }
          } else {
            $("#attachment_div").hide();
            $("#attachment").attr("required", false);
          }
        },
      });

      $("#half_day").on("change", function () {
        if ($(this).is(":checked")) {
          $("#to_date_day_div").hide();

          calendar.settings.multiple = false;
          calendar.pignoseCalendar("set", $('input[name="from_date"]').val());

          console.log(calendar, calendar[0].local);

          $("#to_date_day").val("");
        } else {
          $("#to_date_day_div").show();
          calendar.settings.multiple = true;
        }
      });

      var logic = $('[name="leave_type"]').on("click", function () {
        if ($(this).attr("attachment") == "True") {
          //function that returns the total number of days between from_date and to_date
          function get_total_days(from_date, to_date) {
            var from_date = new Date(from_date);
            var to_date = new Date(to_date);
            var total_days = 0;
            while (from_date <= to_date) {
              total_days++;
              from_date.setDate(from_date.getDate() + 1);
            }
            return total_days;
          }

          total_days = get_total_days(
            $('input[name="from_date"]').val(),
            $('input[name="to_date"]').val()
          );
          console.log(total_days);
          console.log($(this).attr("max_days"));

          if (total_days >= $(this).attr("max_days")) {
            $("#attachment_div").show();
            $("#attachment").attr("required", true);
          } else {
            $("#attachment_div").hide();
            $("#attachment").attr("required", false);
          }
        } else {
          $("#attachment_div").hide();
          $("#attachment").attr("required", false);
        }
      });
    },
  });
});
