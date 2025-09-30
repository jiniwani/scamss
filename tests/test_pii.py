from src.app.utils.pii import mask_pii


def test_phone_masking():
    text = "Call me at +1-555-123-4567"
    result = mask_pii(text)
    assert "555-123-4567" not in result['masked_text']
    assert "[PHONE]" in result['masked_text']


def test_email_masking():
    text = "Email me at scammer@example.com"
    result = mask_pii(text)
    assert "scammer@example.com" not in result['masked_text']
    assert "[EMAIL]" in result['masked_text']


def test_crypto_wallet_masking():
    text = "Send to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    result = mask_pii(text)
    assert "0x742d" not in result['masked_text']
    assert "[CRYPTO_WALLET]" in result['masked_text']


