# -*- mode: python -*-

block_cipher = None


a = Analysis(['EQ2Sheep.py'],
             pathex=['C:\\Users\\Fyang\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'D:\\MyCode\\PyCode\\eq2sheep'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EQ2Sheep',
          debug=False,
          strip=False,
          upx=True,
          console=False )
