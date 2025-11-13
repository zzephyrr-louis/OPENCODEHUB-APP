from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Project, ProjectVersion
import os

User = get_user_model()


class ProfileUpdateTests(TestCase):
    """Unit tests for profile update functionality"""
    
    def setUp(self):
        """Set up test user and client before each test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            bio='Original bio'
        )
        self.client.login(username='testuser', password='testpass123')
        self.update_url = reverse('update_profile')
    
    def tearDown(self):
        """Clean up after each test"""
        # Delete any uploaded profile pictures
        if self.user.profile_picture:
            if os.path.exists(self.user.profile_picture.path):
                os.remove(self.user.profile_picture.path)
    
    # ==================== Basic Profile Update Tests ====================
    
    def test_update_first_name(self):
        """Test updating first name"""
        response = self.client.post(self.update_url, {
            'first_name': 'Updated',
            'last_name': self.user.last_name,
            'bio': self.user.bio
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_update_last_name(self):
        """Test updating last name"""
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': 'NewLastName',
            'bio': self.user.bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, 'NewLastName')
    
    def test_update_bio(self):
        """Test updating bio"""
        new_bio = 'This is my updated bio with more information.'
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': new_bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, new_bio)
    
    def test_update_all_fields(self):
        """Test updating all profile fields at once"""
        response = self.client.post(self.update_url, {
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'bio': 'Completely new bio'
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'NewFirst')
        self.assertEqual(self.user.last_name, 'NewLast')
        self.assertEqual(self.user.bio, 'Completely new bio')
    
    # ==================== Validation Tests ====================
    
    def test_first_name_max_length(self):
        """Test first name exceeds max length (150 chars)"""
        long_name = 'x' * 151
        response = self.client.post(self.update_url, {
            'first_name': long_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio
        })
        
        self.assertEqual(response.status_code, 302)
        # Check that user's name wasn't updated
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, long_name)
    
    def test_last_name_max_length(self):
        """Test last name exceeds max length (150 chars)"""
        long_name = 'y' * 151
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': long_name,
            'bio': self.user.bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.last_name, long_name)
    
    def test_bio_max_length(self):
        """Test bio exceeds max length (500 chars)"""
        long_bio = 'z' * 501
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': long_bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.bio, long_bio)
    
    def test_empty_fields(self):
        """Test updating with empty fields"""
        response = self.client.post(self.update_url, {
            'first_name': '',
            'last_name': '',
            'bio': ''
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(self.user.bio, '')
    
    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from inputs"""
        response = self.client.post(self.update_url, {
            'first_name': '  Trimmed  ',
            'last_name': '  Name  ',
            'bio': '  Bio with spaces  '
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Trimmed')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.bio, 'Bio with spaces')
    
    # ==================== Profile Picture Tests ====================
    
    def test_upload_profile_picture(self):
        """Test uploading a valid profile picture"""
        # Create a simple test image
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile(
            "test_image.gif",
            image_content,
            content_type="image/gif"
        )
        
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
            'profile_picture': image
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture)
    
    def test_upload_invalid_file_type(self):
        """Test uploading non-image file"""
        text_file = SimpleUploadedFile(
            "test.txt",
            b"This is a text file",
            content_type="text/plain"
        )
        
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
            'profile_picture': text_file
        })
        
        self.assertEqual(response.status_code, 302)
        # Profile picture should not be updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)
    
    def test_upload_oversized_file(self):
        """Test uploading file larger than 5MB"""
        # Create a file larger than 5MB (5 * 1024 * 1024 bytes)
        large_content = b'x' * (6 * 1024 * 1024)
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            large_content,
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
            'profile_picture': large_file
        })
        
        self.assertEqual(response.status_code, 302)
        # Profile picture should not be updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)
    
    def test_remove_profile_picture(self):
        """Test removing existing profile picture"""
        # First, add a profile picture
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile("test.gif", image_content, content_type="image/gif")
        self.user.profile_picture = image
        self.user.save()
        
        # Now remove it
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
            'remove_picture': 'true'
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile_picture)
    
    def test_replace_existing_picture(self):
        """Test replacing an existing profile picture"""
        # Upload first picture
        image1 = SimpleUploadedFile(
            "first.gif",
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b',
            content_type="image/gif"
        )
        self.user.profile_picture = image1
        self.user.save()
        old_picture_name = self.user.profile_picture.name
        
        # Upload second picture
        image2 = SimpleUploadedFile(
            "second.gif",
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b',
            content_type="image/gif"
        )
        
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
            'profile_picture': image2
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_picture)
        self.assertNotEqual(self.user.profile_picture.name, old_picture_name)
    
    # ==================== Authentication Tests ====================
    
    def test_update_requires_authentication(self):
        """Test that profile update requires login"""
        self.client.logout()
        response = self.client.post(self.update_url, {
            'first_name': 'Hacker',
            'last_name': 'Name',
            'bio': 'Should not work'
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_get_request_redirects(self):
        """Test that GET request to update_profile redirects"""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 302)
    
    # ==================== Model Method Tests ====================
    
    def test_get_profile_picture_url_with_picture(self):
        """Test get_profile_picture_url with uploaded picture"""
        image = SimpleUploadedFile(
            "test.gif",
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b',
            content_type="image/gif"
        )
        self.user.profile_picture = image
        self.user.save()
        
        url = self.user.get_profile_picture_url()
        self.assertIn('/media/', url)
    
    def test_get_profile_picture_url_without_picture(self):
        """Test get_profile_picture_url returns default"""
        self.user.profile_picture = None
        self.user.save()
        
        url = self.user.get_profile_picture_url()
        self.assertIn('default-profile.svg', url)
    
    def test_get_total_uploads(self):
        """Test upload count calculation"""
        # Create projects
        project1 = Project.objects.create(
            title="Project 1",
            description="Test",
            owner=self.user
        )
        project2 = Project.objects.create(
            title="Project 2",
            description="Test",
            owner=self.user
        )
        
        # Create versions
        ProjectVersion.objects.create(
            project=project1,
            version_number="v1",
            description="Version 1",
            created_by=self.user,
            action='created'
        )
        
        total = self.user.get_total_uploads()
        self.assertEqual(total, 3)  # 2 projects + 1 version
    
    def test_format_upload_count(self):
        """Test upload count formatting"""
        self.assertEqual(User.format_upload_count(15), "15")
        self.assertEqual(User.format_upload_count(1234), "1.2k")
        self.assertEqual(User.format_upload_count(1234567), "1.2M")
        self.assertEqual(User.format_upload_count(999), "999")
        self.assertEqual(User.format_upload_count(1000), "1.0k")
    
    # ==================== Integration Tests ====================
    
    def test_profile_view_displays_updated_data(self):
        """Test that profile view shows updated data"""
        # Update profile
        self.client.post(self.update_url, {
            'first_name': 'Integration',
            'last_name': 'Test',
            'bio': 'Integration test bio'
        })
        
        # View profile
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration')
        self.assertContains(response, 'Test')
        self.assertContains(response, 'Integration test bio')
    
    def test_special_characters_in_bio(self):
        """Test bio with special characters"""
        special_bio = "Bio with special chars: @#$%^&*() <script>alert('xss')</script>"
        response = self.client.post(self.update_url, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': special_bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, special_bio)
    
    def test_unicode_characters_in_name(self):
        """Test name with unicode characters"""
        response = self.client.post(self.update_url, {
            'first_name': 'José',
            'last_name': 'Müller',
            'bio': self.user.bio
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'José')
        self.assertEqual(self.user.last_name, 'Müller')