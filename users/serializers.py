from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates input and creates a new user with hashed password.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'role')

    def validate(self, attrs):
        """
        Validate that passwords match and email is unique.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': "Passwords don't match"
            })
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': "A user with this email already exists"
            })
        
        return attrs

    def create(self, validated_data):
        """
        Create a new user with properly hashed password.
        """
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Create user instance
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Custom serializer for JWT token generation.
    Includes user id and role in the token payload.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate credentials and return JWT tokens with user info.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authenticate user using email instead of username
            user = authenticate(request=self.context.get('request'),
                              username=email,  # Django's authenticate uses username field
                              password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            # Generate tokens (this would be handled by SimpleJWT in the view)
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for profile information.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')
