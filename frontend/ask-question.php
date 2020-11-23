<!DOCTYPE html>
<html lang="en">




<head>

    <!-- meta -->
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Site Title -->
    <title>Ask Question</title>

    <!-- favicon -->
    <link rel="shortcut icon" type="image/x-icon" href="images/icon logo3.png">


    <!-- Bootstrap CSS -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- Font-Awesome CSS -->
    <link href="css/font-awesome.min.css" rel="stylesheet">

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet">

    <!--Animate CSS -->
    <link rel="stylesheet" href="css/animate.min.css">

    <!-- Owl Carousel CSS -->
    <link rel="stylesheet" href="css/owl.carousel.min.css">

    <!-- Mean Menu CSS -->
    <link rel="stylesheet" href="css/meanmenu.min.css">

    <!-- Main Stylesheet -->
    <link href="./css/style.css" rel="stylesheet">

    <!-- Responsive CSS -->
    <link href="css/responsive.css" rel="stylesheet">

    <script src="./js/jquery-3.4.1.min.js"></script>

    <script src="js/load-heder-footer-sidebar.js"></script>

    <script src="//cdn.ckeditor.com/4.15.1/standard/ckeditor.js"></script>

</head>

<body>

    <!-- Start Header -->
    <header id="header"></header>
    <!-- End Header -->

    <!-- Start Page Banner Area -->
    <div class="page-banner-area">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <div class="page-title">
                        <h2>Đặt câu hỏi</h2>
                        <span class="sub-title"><a href="#">Trang chủ </a> / Đặt câu hỏi</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- End Pages Banner Area -->
    <!-- Start Questions Area -->
    <div class="question-area themeix-ptb">
        <div class="container">
            <div class="row">
                <!-- Start Question -->
                <div class="col-md-9">
                    <div class="questions-wrapper">
                        <div class="dwqa-container">
                            <form action="#" class="dwqa-content-edit-form">
                                <label for="question-title">Title</label>
                                <input id="question-title" type="text" name="question-title" />

                                <label for="question-content">Chi tiết câu hỏi</label>
                                <div>
                                    <textarea name="cauhoi" id="cauhoi"></textarea>
                                    <script>
                                        CKEDITOR.replace('cauhoi');
                                    </script>
                                </div>
                                <label for="question-category">Thể loại</label>
                                <select name="question-category" id="question-category" class="postform">
                                    <option value="-1">Chọn loại câu hỏi</option>
                                    <option class="level-0" value="16">Chung</option>
                                    <option class="level-2" value="16">Hỗ trợ</option>
                                    <option class="level-3" value="16">Pre Sale</option>
                                </select>

                                <label for="question-tag">Tag</label>
                                <input id="question-tag" type="text" name="question-tag" />

                                <input id="wp-submit" type="submit" value="Gửi" name="wp-submit" class="themeix-btn hover-bg">
                            </form>
                        </div>
                    </div>
                </div>
                <!-- End Question -->
                <!-- Start Blog Sidebar -->
                <div id="right-blog-sidebar"></div>
                <!-- End Blog Sidebar -->
            </div>
        </div>
    </div>
    <!-- End  Questions Area -->



    <!-- Start Footer Area -->
    <footer id="footer"></footer>
    <!-- End Footer Area -->



    <!-- jquery min -->
    <script src="js/jquery.min.js"></script>

    <!-- Bootstrap Js -->
    <script src="js/bootstrap.min.js"></script>

    <!-- jQuery Easing -->
    <script src="js/jquery.easing.js"></script>

    <!-- Owl Carousel Js -->
    <script src="js/owl.carousel.min.js"></script>

    <!-- Google Map -->
    <script src="https://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>

    <!-- Main Js -->
    <script src="js/main.js"></script>
</body>



</html>