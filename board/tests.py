from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_kim = User.objects.create_user(username='kim', password='kimdjango')
        self.user_park = User.objects.create_user(username='park', password='parkdjango')
        self.user_park.is_staff = True
        self.user_park.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world',
            category=self.category_programming,
            author=self.user_kim,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_park,
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='No category post',
            author=self.user_park,
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_kim,
            content='첫 번째 댓글입니다.'
        )

    def navbar_test(self, soup):
        # navbar 확인
        navbar = soup.nav
        # navbar 문구 확인
        self.assertIn('자유게시판', navbar.text)
        self.assertIn('팀목록&예약', navbar.text)

        logo_btn = navbar.find('a', text='풋살Manager')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='홈')
        self.assertEqual(home_btn.attrs['href'], '/')

        board_btn = navbar.find('a', text='자유게시판')
        self.assertEqual(board_btn.attrs['href'], '/board/')

        about_site_btn = navbar.find('a', text='팀목록&예약')
        self.assertEqual(about_site_btn.attrs['href'], '/about_site/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def test_post_list(self):
        # 포스트가 존재함.
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/board/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('게시물이 존재하지 않습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_kim.username.upper(), main_area.text)
        self.assertIn(self.user_park.username.upper(), main_area.text)

        #포스트가 미존재함.
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/board/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('게시물이 존재하지 않습니다', main_area.text)


    def test_post_detail(self):
        # 포스트가 존재함.

        # 포스트의 url = '/board/1/'
        self.assertEqual(self.post_001.get_absolute_url(), '/board/1/')

        # 상세페이지 테스트(첫번째 페이지)
        # url로 접근하면 정상적으로 작동함을 확인할 수 있음.(status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # post_list페이지와 같은 navbar가 존재함.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 포스트 제목을 웹 브라우저 탭의 title에서 확인가능
        self.assertIn(self.post_001.title, soup.title.text)

        # 포스트 제목이 포스트 영역에 존재
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 포스트 영역에 author 확인가능(구현)
        self.assertIn(self.user_kim.username.upper(), post_area.text)

        # 포스트 영역에 content-내용을 확인가능
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        # 댓글기능 체크
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):

        #비로그인시 , status code 200 불가능하게끔함.(작성이 아예 불가능하게 함.)
        response = self.client.get('/board/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #Non-staff kim이 로그인
        self.client.login(username='kim', password='kimdjango')
        response = self.client.get('/board/create_post/')
        self.assertNotEqual(response.status_code, 200)


        #Staff park이 로그인을 함.
        self.client.login(username='park', password='parkdjango')

        response = self.client.get('/board/create_post/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Create Post - Board', soup.title.next)
        main_area = soup.find('div', id='main-area')

        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/board/create_post/',
            {
                'title': 'Post Form Create',
                'content': "Post Form Page Create",
                'tags_str': 'new tag; Korean Tag, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form Create")
        self.assertEqual(last_post.author.username, 'park')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='Korean Tag'))
        self.assertEqual(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/board/update_post/{self.post_003.pk}/'

        #비로그인시
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        #로그인은함, 작성자는 아님.
        self.assertNotEqual(self.post_003.author, self.user_kim)
        self.client.login(
            username=self.user_kim.username,
            password='kimdjango'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)
        #작성자park
        self.client.login(
            username=self.post_003.author.username,
            password='parkdjango'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Board', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부; python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다. ',
                'content': 'Hello World? We are the one!',
                'category': self.category_music.pk,
                'tags_str': '파이썬 공부; 한글 태그, some tag'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('Hello World? We are the one!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)

        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        # Non-Login Status
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form'))

        # Login status
        self.client.login(username='kim', password='kimdjango')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': "USER KIM의 댓글",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('kim', new_comment_div.text)
        self.assertIn('USER KIM의 댓글', new_comment_div.text)

    def test_comment_update(self):
        comment_by_park = Comment.objects.create(
            post=self.post_001,
            author=self.user_park,
            content='USER PARK의 댓글.'
        )

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        # Login status
        self.client.login(username='kim', password='kimdjango')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/board/update_comment/1/')

        response = self.client.get('/board/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Board', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)

        response = self.client.post(
            f'/board/update_comment/{self.comment_001.pk}/',
            {
                'content': "KIM의 댓글수정",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('KIM의 댓글수정', comment_001_div.text)
        self.assertIn('Updated: ', comment_001_div.text)

    def test_delete_comment(self):
        comment_by_park = Comment.objects.create(
            post=self.post_001,
            author=self.user_park,
            content='USER PARK의 댓글.'
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        # Non-login
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn'))

        # Login status(park)
        self.client.login(username='park', password='parkdjango')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        comment_002_delete_modal_btn = comment_area.find(
            'a', id='comment-2-delete-modal-btn'
        )
        self.assertIn('delete', comment_002_delete_modal_btn.text)
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are You Sure?', delete_comment_modal_002.text)
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(
            really_delete_btn_002.attrs['href'],
            '/board/delete_comment/2/'
        )

        response = self.client.get('/board/delete_comment/2/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('USER PARK의 댓글.', comment_area.text)

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

    def test_search(self):
        post_about_python = Post.objects.create(
            title='파이썬 포스트.',
            content='Hello World. We are the world.',
            author=self.user_kim
        )

        response = self.client.get('/board/search/파이썬/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')

        self.assertIn('Search: 파이썬 (2)', main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_python.title, main_area.text)