import { foundation } from 'foundation-sites/js/foundation.core';
import 'foundation-sites/js/foundation.util.mediaQuery';
import 'foundation-sites/js/foundation.sticky.js';
import 'foundation-sites/js/foundation.reveal';
import 'foundation-sites/js/foundation.util.keyboard';
import 'foundation-sites/js/foundation.util.box';
import 'foundation-sites/js/foundation.util.timerAndImageLoader.js';
import 'foundation-sites/js/foundation.util.triggers';
import 'foundation-sites/js/foundation.util.motion';
import 'foundation-sites/js/foundation.tabs.js';

var jQuery = require('jquery');
var Chart = require('chart.js');
var tablesorter = require('tablesorter');

import 'datatables.net';
import dt from 'datatables.net-zf';
import buttons from 'datatables.net-buttons-zf';
import autofill from 'datatables.net-autofill-zf';
import colreorder from 'datatables.net-colreorder';
import responsive from 'datatables.net-responsive-zf'


import '!style!css!datatables.net-zf/css/dataTables.foundation.css';
import '!style!css!datatables.net-buttons-zf/css/buttons.foundation.css';
import '!style!css!datatables.net-autofill-zf/css/autoFill.foundation.css';
import '!style!css!datatables.net-colreorder-zf/css/colReorder.foundation.css';
//import 'file-loader?name=img/[name].[hash].[ext]!datatables.net-zf/images/sort_asc.png';
//import 'datatables.net-zf/images/sort_asc_disabled.png';
//import 'datatables.net-zf/images/sort_both.png';
//import 'datatables.net-zf/images/sort_desc.png';
//import 'datatables.net-zf/images/sort_desc_disabled.png';

//var dt = require( 'datatables.net-zf' );
//var buttons = require( 'datatables.net-buttons-zf' );
dt(window, $);
buttons(window, $);
autofill(window, $);
colreorder(window, $);
responsive(window, $);

$.fn.foundation = foundation;

$(document).ready(function() {
      $(document).foundation();
   });


$(document).ready(function() {
  $('#transactions-table').DataTable({
    "iDisplayLength": 25
  });
});

$(document).ready(function(){
  $(".close-button").click(function(){
      $(".flex-container-close").remove();
    });

  $("#budget").click(function(){
    window.location.replace($SCRIPT_ROOT + '/budget');
  });

  $("#transactions").click(function() {
    window.location.replace($SCRIPT_ROOT + '/transactions');
  });

  $("#buckets").click(function() {
    window.location.replace($SCRIPT_ROOT + '/buckets');
  });

  $("#create-budget").click(function(){
    $(".modal").css("display", "flex");
  });

  $(".closebtn").click(function(){
    $(".modal").css("display", "none");
  });

  $("#create-budget").click(function(){
      $("#userbudgetcategory").prop("disabled", true);
      $("#userbudgetcategory").val("");
      $("#budgetcategory").val(0);
      $(".subcategory-select-field option").remove();
  });


  $(".category-select-field").on('change', function(){
    var selected = $(".category-select-field option:selected").val()
    $.getJSON($SCRIPT_ROOT + '/_subcategory', {
      categoryid: $(".category-select-field option:selected").val()
    }, function(data){
      $(".subcategory-select-field option").remove();
      $.each(data, function(){
        $(".subcategory-select-field").append($("<option />").val(this[0]).text(this[1]));
      });
      if (selected == 0) {
        $("#userbudgetcategory").prop("disabled", true);
        $("#userbudgetcategory").val("");
      } else if ((selected != 0) && ($(".subcategory-select-field option:selected").val() == 0)) {
        $("#userbudgetcategory").prop("disabled", false);
      } else {
        $("#userbudgetcategory").prop("disabled", true);
      }
    });
    return false;
  });



  $(".subcategory-select-field").on('change', function(){
    var selected = $(".subcategory-select-field option:selected").val()
    if(selected == 0) {
      $("#userbudgetcategory").prop("disabled", false);
    } else {
      $("#userbudgetcategory").prop("disabled", true);
      $("#userbudgetcategory").val("");
    };
  });

  $("#upload-file").click(function(){
    $(".modal").css("display", "flex");
  });

  $(".closebtn").click(function(){
    $(".modal").css("display", "none");
  });

});

$(document).ready(function() {
  $("#myTable").tablesorter();
});

$(function () {
  if ($SCRIPT_URL == '/budget'){
  $.getJSON($SCRIPT_ROOT + '/_get_budget', {}, function (data) {
    var budgetData = JSON.parse(data);
    $(".progress-meter").each(function () {
      var divId = $(this).attr('id');
      var parentDivId = $("#" + divId).parent().attr('id');
      var percentageValue = budgetData.totaltransactionamount[divId] * -1 / budgetData.totalbudgetamount[divId] * 100;
      var percentage = percentageValue + '%';
      if (percentageValue > 100) {
        $("#" + parentDivId).attr('aria-valuenow', 100)
        $("#" + parentDivId).attr('aria-valuetext', "100 percent")
        $("#" + divId).css("width", "100%");
        $("#" + parentDivId).addClass("alert");
      } else if (percentageValue > 80){
        $("#" + parentDivId).attr('aria-valuenow', percentageValue)
        $("#" + parentDivId).attr('aria-valuetext', percentageValue + " percent")
        $("#" + divId).css("width", percentage);
        $("#" + parentDivId).addClass("warning");
      } else {
        $("#" + parentDivId).attr('aria-valuenow', percentageValue)
        $("#" + parentDivId).attr('aria-valuetext', percentageValue + " percent")
        $("#" + divId).css("width", percentage);
        $("#" + parentDivId).addClass("success");
      };
    });
  });
  return false;
}
});

/*Chart.js chartss*/

var colorArray = ["#4d4dff", "#ff4d4d", "#4dff88", "#4dc3ff", "#ff4dff", "#ffc34d", "#b8b894"];



$(document).ready(function () {
  if ($SCRIPT_URL == '/buckets') {
    Chart.defaults.global.maintainAspectRatio = false;
    $.getJSON($SCRIPT_ROOT + '/_get_buckets', {}, function (data) {
      var bucketData = JSON.parse(data);
      console.log(bucketData);
      var bucketNameArray = Object.keys(bucketData['Bucket Name']).map(function (k) {
        return bucketData['Bucket Name'][k];
      });
      var bucketAmountArray = Object.keys(bucketData.Amount).map(function (k) {
        return bucketData.Amount[k];
      });
      var arrayLength = bucketNameArray.length;
      var backgroundColorArray = colorArray.slice(0, arrayLength);
      var ctx = $("#bucketPieChart");
      var chartData = {
        labels: bucketNameArray,
        datasets: [{
          data: bucketAmountArray,
          backgroundColor: backgroundColorArray,
          hoverBackgroundColor: backgroundColorArray
        }]
      };
      var chartOptions = {
        responsive: true,
        //circumference: Math.PI * 4.0,
        animation: {
          animateRotate: true,
          animateScale: true
        }
      };
      createPieChart(ctx, chartData, chartOptions);
    });
    function createPieChart(ctx, chartData, chartOptions) {
      var basePieChart = new Chart(ctx, {
      type: 'pie',
      data: chartData,
      options: chartOptions
      });
      clickFunction(basePieChart);
    };
    function clickFunction(basePieChart) {
      $("#bucketPieChart").click(function (event) {
        var activePoints = basePieChart.getElementsAtEvent(event);
        //console.log(basePieChart);
        console.log(activePoints);
        var bucketName = activePoints[0]._model.label
        $.getJSON($SCRIPT_ROOT + '/_drill_buckets', {
          bucket_name: bucketName
        }, function (data) {
          var drillData = JSON.parse(data);
          console.log(drillData);
          basePieChart.destroy();

          var bucketName = drillData['Bucket Name'][0];
          var bucketAmount = drillData.Amount[0];
          var bucketGoalAmount = drillData['Goal Amount'][0];

          if (bucketGoalAmount != null) {
            var remainingGoal = bucketGoalAmount - bucketAmount;
          } else {
            remainingGoal = 0;
          };

          var bucketNameArray = [];
          bucketNameArray.push(bucketName, 'Remaining Goal');
          //console.log(bucketNameArray);
          var bucketAmountArray = [];
          bucketAmountArray.push(bucketAmount, remainingGoal);
          //console.log(bucketAmountArray);
          var arrayLength = bucketNameArray.length;
          var backgroundColorArray = colorArray.slice(0, arrayLength);
          var ctx = $("#bucketPieChart");
          var chartData = {
            labels: bucketNameArray,
            datasets: [{
              data: bucketAmountArray,
              backgroundColor: backgroundColorArray,
              hoverBackgroundColor: backgroundColorArray
            }]
          };
          var chartOptions = {
            responsive: true,
            //circumference: Math.PI * 4.0,
            animation: {
              animateRotate: true,
              animateScale: true
            }
          };
          createPieChart(ctx, chartData, chartOptions);

        });
      });
    };
  };
});
