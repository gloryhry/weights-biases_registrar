import random
import string

def generate_random_string(min_length: int = 4, max_length: int = 10) -> str:
    """
    生成指定长度范围内的随机字符串
    
    Args:
        min_length (int): 最小长度，默认为4
        max_length (int): 最大长度，默认为10
        
    Returns:
        str: 生成的随机字符串
    """
    # 确保长度在有效范围内
    if min_length < 1:
        min_length = 1
    if max_length < min_length:
        max_length = min_length
    
    # 生成随机长度
    length = random.randint(min_length, max_length)
    
    # 生成随机字符串（包含字母和数字）
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))