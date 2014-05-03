
<?php
include("php_file_tree.php");
?>
<!DOCTYPE html>

<html><head>
    
  <meta http-equiv="Content-Type" content="text/html;charset=windows-1251" />
    <meta xmlns="" name="KEYWORDS" content="">
 <link href="css\bootstrap.css" rel="stylesheet">
 
  
     <meta xmlns="" name="KEYWORDS" content="">
    <link href="styles/default/default.css" rel="stylesheet" type="text/css" media="screen" />
     <script type="text/javascript" src="http://d3js.org/d3.v3.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.0.6/angular.min.js"></script>
<script src="reusable_chart.js"></script>

  
 
   <script src="php_file_tree.js" type="text/javascript"></script>
     <style type="text/css">

      body {
        padding-top: 20px;
        padding-bottom: 60px;
        background-color: #f5f5f5;
      }

      
      .container {
        margin: 0 auto;
        max-width: 1000px;
      }
      .container > hr {
        margin: 60px 0;
      }

      
      .navbar .navbar-inner {
        padding: 0;
      }
      .navbar .nav {
        margin: 0;
        display: table;
        width: 100%;
      }
      .navbar .nav li {
        display: table-cell;
        width: 1%;
        float: none;
      }
      .navbar .nav li a {
        font-weight: bold;
        text-align: center;
        border-left: 1px solid rgba(255,255,255,.75);
        border-right: 1px solid rgba(0,0,0,.1);
      }
      .navbar .nav li:first-child a {
        border-left: 0;
        border-radius: 3px 0 0 3px;
      }
      .navbar .nav li:last-child a {
        border-right: 0;
        border-radius: 0 3px 3px 0;
      }
      
    {
            font: 14px sans-serif;
        }
        .axis path, .axis line {
            fill: none;
            stroke: black;
            shape-rendering: crispEdges;
        }
        .axis path{
            fill: none;
            stroke: none;
        }
        .bar {
            fill: steelblue;

        }
    </style>

   
   
   
  </head>


  <body>

    <div class="container">

      <div class="masthead">
        <h3 class="muted">Project name</h3>
        <div class="navbar">
          <div class="navbar-inner">
            <div class="container">
              <ul class="nav">
                <li class="active"><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">Home</a></li>
                <li><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">Projects</a></li>
                <li><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">Services</a></li>
                <li><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">Downloads</a></li>
                <li><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">About</a></li>
                <li><a href="http://getbootstrap.com/2.3.2/examples/justified-nav.html#">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
 
 <div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <!--Sidebar content-->
       <?php
    
   
    echo php_file_tree("files", "[link]");
    
    ?>
    </div>
    <div class="span10">
     <div style='width: 100px;
    height: 100px;
    
    position: relative;
    top:0;
    bottom: 0;
    left: 0;
    right: 0;

    margin: auto;'>
     <div>
    <div ng-app="charts">
    <div ng-controller="mainCtrl">
        <chart-form></chart-form>
        <bar-chart height="options.height" data="data" hovered="hovered(args)"></bar-chart>
        <!--<bar-chart height="300" data="data" hovered="hovered(args)></bar-chart>-->
    </div>
</div>


<script>
    angular.module('charts', [])
        .controller('mainCtrl', function AppCtrl ($scope) {
            $scope.options = {width: 500, height: 300, 'bar': 'aaa'};
            $scope.data = [0, 0, 0, 0];
            $scope.hovered = function(d){
                $scope.barValue = d;
                $scope.$apply();
            };
            $scope.barValue = 'None';
        })
        .directive('barChart', function(){
            var chart = d3.custom.barChart();
            return {
                restrict: 'E',
                replace: true,
                template: '<div class="chart"></div>',
                scope:{
                    height: '=height',
                    data: '=data',
                    hovered: '&hovered'
                },
                link: function(scope, element, attrs) {
                    var chartEl = d3.select(element[0]);
                    chart.on('customHover', function(d, i){
                        scope.hovered({args:d});
                    });

                    scope.$watch('data', function (newVal, oldVal) {
                        chartEl.datum(newVal).call(chart);
                    });

                    scope.$watch('height', function(d, i){
                        chartEl.call(chart.height(scope.height));
                    })
                }
            }
        })
        .directive('chartForm', function(){
            return {
                restrict: 'E',
                replace: true,
                controller: function AppCtrl ($scope) {
                    $scope.update = function(d, i){ $scope.data = [100,20,30]};
                    
                },

                template: '<div class="form">' +
                        'Height: {{options.height}}<br />' +
                        '<input type="range" ng-model="options.height" min="100" max="800"/>' +
                        '<br />Node Viste statistics: {{barValue}}' +
                        '<br/><button ng-click="update()">Update Data</button>' +
                        '</div>'

            }

        });

</script>
    </div>
  </div>
</div>
    

      </div>
    </div>
 </div>

       
        
    
      

      

  
   


  
</body>
</html>
