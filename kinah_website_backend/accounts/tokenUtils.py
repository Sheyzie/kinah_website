from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken, 
    BlacklistedToken
)

User = get_user_model()


def get_active_sessions(user):
    """
    Get all active sessions (non-blacklisted tokens) for a user
    """
    outstanding = OutstandingToken.objects.filter(user=user)
    blacklisted_jtis = BlacklistedToken.objects.values_list('token__jti', flat=True)
    
    active_tokens = []
    for token in outstanding:
        if token.jti not in blacklisted_jtis:
            active_tokens.append({
                'jti': token.jti,
                'created_at': token.created_at,
                'expires_at': token.expires_at
            })
    
    return active_tokens


def revoke_all_tokens(user):
    """
    Revoke all tokens for a user (useful for security incidents)
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    tokens = OutstandingToken.objects.filter(user=user)
    revoked_count = 0
    
    for token in tokens:
        try:
            RefreshToken(token.token).blacklist()
            revoked_count += 1
        except Exception:
            pass
    
    return revoked_count


def get_token_statistics():
    """
    Get statistics about tokens in the system
    """
    total_outstanding = OutstandingToken.objects.count()
    total_blacklisted = BlacklistedToken.objects.count()
    active_tokens = total_outstanding - total_blacklisted
    
    return {
        'total_outstanding': total_outstanding,
        'total_blacklisted': total_blacklisted,
        'active_tokens': active_tokens,
        'blacklist_rate': (total_blacklisted / total_outstanding * 100) if total_outstanding > 0 else 0
    }