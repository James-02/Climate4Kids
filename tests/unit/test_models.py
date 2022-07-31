from tests.conftest import new_user

def test_new_user_with_fixture(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, authenticated, and role fields are defined correctly
    """
    assert new_user.username == 'testing123@gmail.com'
    assert new_user.password != 'testing12345'
    assert new_user.role == 'user'
