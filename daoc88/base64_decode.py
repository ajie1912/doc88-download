import execjs

"""此加密过程为js实现，python与js语法有差异，比较难实现相同作用"""
ctx = execjs.compile("""
    function all(str){
    var m_END_OF_INPUT = -1;
    var m_base64Chars_r = new Array(
            'P','J','K','L','M','N','O','I',
            '3','y','x','z','0','1','2','w',
            'v','p','r','q','s','t','u','o',
            'B','H','C','D','E','F','G','A',
            'h','n','i','j','k','l','m','g',
            'f','Z','a','b','c','d','e','Y',
            'X','R','S','T','U','V','W','Q',
            '!','5','6','7','8','9','+','4'
    );
    var m_reverseBase64Chars = new Array(128);
    for (var i=0; i < m_base64Chars_r.length; i++)
    {
        m_reverseBase64Chars[m_base64Chars_r[i]] = i;
    }

    var m_base64Str;
    var m_base64Count;
    function m_setBase64Str(str)
    {
        m_base64Str = str;
        m_base64Count = 0;
    }
    function m_readBase64()
    {
        if (!m_base64Str) return m_END_OF_INPUT;
        if (m_base64Count >= m_base64Str.length) return m_END_OF_INPUT;
        var c = m_base64Str.charCodeAt(m_base64Count) & 0xff;
        m_base64Count++;
        return c;
    }

    function m_readReverseBase64()
    {
        if (!m_base64Str) return m_END_OF_INPUT;
        while (true)
        {
            if (m_base64Count >= m_base64Str.length) return m_END_OF_INPUT;
            var nextCharacter = m_base64Str.charAt(m_base64Count);
            m_base64Count++;
            if (m_reverseBase64Chars[nextCharacter])
            {
                return m_reverseBase64Chars[nextCharacter];
            }
            if (nextCharacter == 'P') return 0;
        }
        return m_END_OF_INPUT;
    }

    function m_ntos(n)
    {
        n = n.toString(16);
        if (n.length == 1) n = "0" + n;
        n = "%" + n;
        return unescape(n);
    }

    function m_decodeBase64(str)
    {
        m_setBase64Str(str);
        var result = "";
        var inBuffer = new Array(4);
        var done = false;
        while (!done && (inBuffer[0] = m_readReverseBase64()) != m_END_OF_INPUT&& (inBuffer[1] = m_readReverseBase64()) != m_END_OF_INPUT){
            inBuffer[2] = m_readReverseBase64();
            inBuffer[3] = m_readReverseBase64();
            result += m_ntos((((inBuffer[0] << 2) & 0xff)| inBuffer[1] >> 4));
            if (inBuffer[2] != m_END_OF_INPUT){
                result +=  m_ntos((((inBuffer[1] << 4) & 0xff)| inBuffer[2] >> 2));
                if (inBuffer[3] != m_END_OF_INPUT){
                    result +=  m_ntos((((inBuffer[2] << 6)  & 0xff) | inBuffer[3]));
                } else {
                    done = true;
                }
            } else {
                done = true;
            }
        }
        result = m_utf8to16(result);
        return result;
    }
    function m_utf16to8(str) {
        var out, i, len, c;
        out = "";
        len = str.length;
        for(i = 0; i < len; i++) {
            c = str.charCodeAt(i);
            if ((c >= 0x0001) && (c <= 0x007F)) {
                out += str.charAt(i);
            } else if (c > 0x07FF) {
                out += String.fromCharCode(0xE0 | ((c >> 12) & 0x0F));
                out += String.fromCharCode(0x80 | ((c >>  6) & 0x3F));
                out += String.fromCharCode(0x80 | ((c >>  0) & 0x3F));
            } else {
                out += String.fromCharCode(0xC0 | ((c >>  6) & 0x1F));
                out += String.fromCharCode(0x80 | ((c >>  0) & 0x3F));
            }
        }
        return out;
    }

    function m_utf8to16 (str)
    {
        var out, i, len, c;
        var char2, char3;
        out = "";
        len = str.length;
        i = 0;
        while(i < len) {
            c = str.charCodeAt(i++);
            switch(c >> 4)
            {
                case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
                out += str.charAt(i-1);
                break;
                case 12: case 13:
                char2 = str.charCodeAt(i++);
                out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
                break;
                case 14:
                    char2 = str.charCodeAt(i++);
                    char3 = str.charCodeAt(i++);
                    out += String.fromCharCode(((c & 0x0F) << 12) |
                            ((char2 & 0x3F) << 6) |
                            ((char3 & 0x3F) << 0));
                    break;
            }
        }

        return out;
    }
    return  m_decodeBase64(str)
    }
""")



