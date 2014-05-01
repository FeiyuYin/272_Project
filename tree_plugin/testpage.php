<?php
include("php_file_tree.php");
?>
<!DOCTYPE html>

<html><head>
    
  <meta http-equiv="Content-Type" content="text/html;charset=windows-1251" />
    <meta xmlns="" name="KEYWORDS" content="">
 <link href="/static/assets/bootstrap_2.css" rel="stylesheet">
 
  
     <meta xmlns="" name="KEYWORDS" content="">
    <link href="/static/assets/default.css" rel="stylesheet" type="text/css" media="screen" />
    
    <!-- Makes the file tree(s) expand/collapsae dynamically -->
    <script src="/static/assets/php_file_tree.js" type="text/javascript"></script>
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
                <li><a href="/index/">Home</a></li>
                <li class="active"><a href="#">MyWebApps</a></li>
                <li><a href="#">Services</a></li>
                <li><a href="#">Downloads</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

     <?php
    
    // This links the user to http://example.com/?file=filename.ext
    //echo php_file_tree($_SERVER['DOCUMENT_ROOT'], "http://example.com/?file=[link]/");

    // This links the user to http://example.com/?file=filename.ext and only shows image files
    //$allowed_extensions = array("gif", "jpg", "jpeg", "png");
    //echo php_file_tree($_SERVER['DOCUMENT_ROOT'], "http://example.com/?file=[link]/", $allowed_extensions);
    
    // This displays a JavaScript alert stating which file the user clicked on
    //echo php_file_tree(".", "javascript:alert('You clicked on [link]');");
    echo php_file_tree("WebApp1", "[link]");
    
    ?>
    

      

      

    </div> 
    
<div class="footer">
        <p>@Company 2013</p>
      </div>
  

</body></html>
