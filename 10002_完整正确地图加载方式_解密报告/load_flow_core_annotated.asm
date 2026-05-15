
### LoadMap_sub_1001AC70 0x1001ac70
0x1001ac70: push     -1
0x1001ac72: push     0x102ac2e8
0x1001ac77: mov      eax, dword ptr fs:[0]
0x1001ac7d: push     eax
0x1001ac7e: sub      esp, 0x23c
0x1001ac84: mov      eax, dword ptr [0x10367584]
0x1001ac89: xor      eax, esp
0x1001ac8b: mov      dword ptr [esp + 0x238], eax
0x1001ac92: push     ebp
0x1001ac93: push     esi
0x1001ac94: push     edi
0x1001ac95: mov      eax, dword ptr [0x10367584]
0x1001ac9a: xor      eax, esp
0x1001ac9c: push     eax
0x1001ac9d: lea      eax, [esp + 0x24c]
0x1001aca4: mov      dword ptr fs:[0], eax
0x1001acaa: mov      eax, dword ptr [esp + 0x260]
0x1001acb1: cmp      eax, 6
0x1001acb4: mov      esi, dword ptr [esp + 0x25c]
0x1001acbb: mov      edi, ecx
0x1001acbd: ja       0x1001b417
0x1001acc3: jmp      dword ptr [eax*4 + 0x1001b448]
0x1001acca: lea      eax, [esp + 0x10]
0x1001acce: push     eax
0x1001accf: lea      ecx, [esp + 0x18]
0x1001acd3: push     ecx
0x1001acd4: lea      edx, [esp + 0x24]
0x1001acd8: push     edx
0x1001acd9: lea      eax, [esp + 0x24]
0x1001acdd: push     eax
0x1001acde: call     0x10165d50
0x1001ace3: mov      ecx, dword ptr [esp + 0x20]
0x1001ace7: mov      edx, dword ptr [esp + 0x24]
0x1001aceb: mov      eax, dword ptr [esp + 0x2c]
0x1001acef: push     ecx
0x1001acf0: mov      ecx, dword ptr [esp + 0x2c]
0x1001acf4: push     edx
0x1001acf5: push     eax
0x1001acf6: push     ecx
0x1001acf7: call     0x10165fe0
0x1001acfc: mov      edx, dword ptr [0x1036fca8]
0x1001ad02: mov      eax, dword ptr [edx + 8]
0x1001ad05: mov      esi, dword ptr [0x102ce458]
0x1001ad0b: add      esp, 0x20
0x1001ad0e: push     0
0x1001ad10: push     0x28
0x1001ad12: push     0x1788
0x1001ad17: push     eax
0x1001ad18: call     esi
0x1001ad1a: mov      eax, dword ptr [0x10585800]
0x1001ad1f: test     eax, eax
0x1001ad21: je       0x1001ad2e
0x1001ad23: push     0x102d0504 ; "读取地形和障碍信息"
0x1001ad28: push     0x1e
0x1001ad2a: push     0
0x1001ad2c: call     eax
0x1001ad2e: push     0x102d0504 ; "读取地形和障碍信息"
0x1001ad33: push     0x1e
0x1001ad35: mov      dword ptr [edi + 0x7a4], 0
0x1001ad3f: call     0x10077c20
0x1001ad44: mov      ecx, dword ptr [0x1036fca8]
0x1001ad4a: mov      edx, dword ptr [ecx + 8]
0x1001ad4d: add      esp, 8
0x1001ad50: push     0
0x1001ad52: push     0x32
0x1001ad54: push     0x1788
0x1001ad59: push     edx
0x1001ad5a: call     esi
0x1001ad5c: jmp      0x1001b417
0x1001ad61: mov      eax, dword ptr [0x10589968]
0x1001ad66: push     esi
0x1001ad67: push     eax
0x1001ad68: push     0x102d04e8 ; "[%d] begin load map[%s]\n"
0x1001ad6d: push     0x102cea84 ; "init"
0x1001ad72: call     0x10115fb0
0x1001ad77: add      esp, 0x10
0x1001ad7a: lea      ecx, [edi + 0xc1c]
0x1001ad80: call     0x10019750
0x1001ad85: mov      eax, dword ptr [0x1036fdb0]
0x1001ad8a: test     eax, eax
0x1001ad8c: jne      0x1001ae1b
0x1001ad92: lea      ecx, [esp + 0x3c]
0x1001ad96: call     0x10019250 ; "嬃3珊"
0x1001ad9b: push     esi
0x1001ad9c: lea      ecx, [esp + 0x60]
0x1001ada0: mov      dword ptr [esp + 0x258], 0
0x1001adab: call     0x100017d0
0x1001adb0: push     1
0x1001adb2: push     0x1fa0
0x1001adb7: mov      dword ptr [esp + 0x80], 0x7d0
0x1001adc2: mov      dword ptr [esp + 0x84], 0xfa0
0x1001adcd: mov      dword ptr [esp + 0x8c], 0xa
0x1001add8: call     0x10002810 ; "V媡$兤V鑇{&"
0x1001addd: add      esp, 8
0x1001ade0: mov      dword ptr [esp + 0x18], eax
0x1001ade4: test     eax, eax
0x1001ade6: mov      byte ptr [esp + 0x254], 1
0x1001adee: je       0x1001adfe
0x1001adf0: lea      ecx, [esp + 0x3c]
0x1001adf4: push     ecx
0x1001adf5: mov      ecx, eax
0x1001adf7: call     0x10070120
0x1001adfc: jmp      0x1001ae00
0x1001adfe: xor      eax, eax
0x1001ae00: lea      ecx, [esp + 0x3c]
0x1001ae04: mov      dword ptr [0x1036fdb0], eax
0x1001ae09: mov      dword ptr [esp + 0x254], 0xffffffff
0x1001ae14: call     0x10019300
0x1001ae19: jmp      0x1001ae4f
0x1001ae1b: lea      ecx, [eax + 0x18]
0x1001ae1e: call     0x1006bbf0
0x1001ae23: mov      ecx, dword ptr [0x1036fdb0]
0x1001ae29: call     0x10071260
0x1001ae2e: mov      ecx, dword ptr [0x1036fdb0]
0x1001ae34: push     esi
0x1001ae35: add      ecx, 0x1e78
0x1001ae3b: call     0x100017d0
0x1001ae40: mov      ecx, dword ptr [0x1036fca8]
0x1001ae46: test     ecx, ecx
0x1001ae48: je       0x1001ae4f
0x1001ae4a: call     0x1012ba30
0x1001ae4f: mov      ecx, dword ptr [0x1036fdb0]
0x1001ae55: push     0
0x1001ae57: push     0
0x1001ae59: push     0
0x1001ae5b: call     0x10070980
0x1001ae60: test     al, al
0x1001ae62: jne      0x1001ae8f
0x1001ae64: push     esi
0x1001ae65: push     0x102d01c8 ; "msg读取地图[%s]失败, 游戏退出!\n"
0x1001ae6a: push     0x102cead4 ; "error"
0x1001ae6f: call     0x10115fb0
0x1001ae74: add      esp, 0xc
0x1001ae77: push     0x102d01b8 ; "读取地图失败"
0x1001ae7c: push     9
0x1001ae7e: mov      ecx, 0x10383f30
0x1001ae83: call     0x100f66f0
0x1001ae88: push     0
0x1001ae8a: call     0x10264143
0x1001ae8f: mov      edx, dword ptr [0x1036fdb0]
0x1001ae95: mov      ecx, 0xfffffff6
0x1001ae9a: mov      dword ptr [edx + 0x1a58], ecx
0x1001aea0: mov      edx, dword ptr [0x1036fdb0]
0x1001aea6: mov      eax, 0x100
0x1001aeab: mov      dword ptr [edx + 0x1a60], eax
0x1001aeb1: mov      edx, dword ptr [0x1036fdb0]
0x1001aeb7: mov      dword ptr [edx + 0x1a5c], ecx
0x1001aebd: mov      ecx, dword ptr [0x1036fdb0]
0x1001aec3: push     0x102d04d4 ; "接受地图运行数据"
0x1001aec8: push     0x28
0x1001aeca: mov      dword ptr [ecx + 0x1a58], eax
0x1001aed0: call     0x10077c20
0x1001aed5: push     0x102d04d4 ; "接受地图运行数据"
0x1001aeda: call     0x102647a4
0x1001aedf: mov      edx, dword ptr [0x1036fca8]
0x1001aee5: mov      eax, dword ptr [edx + 8]
0x1001aee8: add      esp, 0xc
0x1001aeeb: push     0
0x1001aeed: push     0x3c
0x1001aeef: push     0x1788
0x1001aef4: push     eax
0x1001aef5: call     dword ptr [0x102ce458]
0x1001aefb: mov      eax, dword ptr [0x10585800]
0x1001af00: test     eax, eax
0x1001af02: je       0x1001b417
0x1001af08: push     0x102d04d4 ; "接受地图运行数据"
0x1001af0d: push     0x28
0x1001af0f: jmp      0x1001b413
0x1001af14: mov      esi, dword ptr [0x102ce458]
0x1001af1a: xor      ebp, ebp
0x1001af1c: cmp      dword ptr [0x1035f270], ebp
0x1001af22: je       0x1001af84
0x1001af24: cmp      dword ptr [edi + 0xc4c], ebp
0x1001af2a: je       0x1001af84
0x1001af2c: mov      eax, dword ptr [edi + 8]
0x1001af2f: lea      ecx, [esp + 0x14]
0x1001af33: push     ecx
0x1001af34: lea      edx, [esp + 0x14]
0x1001af38: push     edx
0x1001af39: push     0x53a
0x1001af3e: push     eax
0x1001af3f: mov      dword ptr [esp + 0x20], ebp
0x1001af43: mov      dword ptr [esp + 0x24], ebp
0x1001af47: call     esi
0x1001af49: cmp      dword ptr [esp + 0x10], ebp
0x1001af4d: jne      0x1001af56
0x1001af4f: xor      eax, eax
0x1001af51: jmp      0x1001b41c ; "媽$L"
0x1001af56: mov      ecx, dword ptr [esp + 0x14]
0x1001af5a: push     ecx
0x1001af5b: push     0x102d04a4 ; "成功接受到HostServer发来的脚本数据, size = %d!\n"
0x1001af60: push     0x102cea84 ; "init"
0x1001af65: call     0x10115fb0
0x1001af6a: mov      edx, dword ptr [esp + 0x20]
0x1001af6e: mov      eax, dword ptr [esp + 0x1c]
0x1001af72: mov      ecx, dword ptr [0x10377d08]
0x1001af78: push     ebp
0x1001af79: push     edx
0x1001af7a: push     eax
0x1001af7b: push     ecx
0x1001af7c: call     0x101fc730 ; "婦$婰$婽$V媡$WPQRV鑥6"
0x1001af81: add      esp, 0x1c
0x1001af84: push     0x102d0490 ; "读取角色和物件信息"
0x1001af89: push     0x3c
0x1001af8b: call     0x10077c20
0x1001af90: push     0x102d0490 ; "读取角色和物件信息"
0x1001af95: call     0x102647a4
0x1001af9a: mov      edx, dword ptr [0x1036fca8]
0x1001afa0: mov      eax, dword ptr [edx + 8]
0x1001afa3: add      esp, 0xc
0x1001afa6: push     ebp
0x1001afa7: push     0x46
0x1001afa9: push     0x1788
0x1001afae: push     eax
0x1001afaf: call     esi
0x1001afb1: mov      eax, dword ptr [0x10585800]
0x1001afb6: cmp      eax, ebp
0x1001afb8: je       0x1001b417
0x1001afbe: push     0x102d0490 ; "读取角色和物件信息"
0x1001afc3: push     0x32
0x1001afc5: push     ebp
0x1001afc6: jmp      0x1001b415
0x1001afcb: cmp      dword ptr [0x1036fcec], 0
0x1001afd2: je       0x1001b0a7
0x1001afd8: cmp      dword ptr [0x1036fcf0], 0
0x1001afdf: je       0x1001b07a ; "VV峊$Dh"
0x1001afe5: push     0x102d0480 ; "Load_Tab...\n"
0x1001afea: call     0x102647a4
0x1001afef: push     esi
0x1001aff0: push     0x102d047c
0x1001aff5: push     0x102d0470 ; "Load_Tab"
0x1001affa: call     0x100790b0
0x1001afff: mov      ecx, dword ptr [0x10589968]
0x1001b005: push     ecx
0x1001b006: push     0x102d0444 ; "[%d] 开始执行地图脚本, 读取物件和角色信息!\n"
0x1001b00b: push     0x102cea84 ; "init"
0x1001b010: call     0x10115fb0
0x1001b015: push     esi
0x1001b016: push     esi
0x1001b017: lea      edx, [esp + 0xac]
0x1001b01e: push     0x102d0430 ; "map/%s/%s_init.lua"
0x1001b023: push     edx
0x1001b024: call     0x10263225
0x1001b029: lea      eax, [esp + 0xb4]
0x1001b030: push     eax
0x1001b031: push     0x102d0420 ; "Load [%s]...\n"
0x1001b036: call     0x102647a4
0x1001b03b: lea      ecx, [esp + 0xbc]
0x1001b042: push     ecx
0x1001b043: call     0x10016ab0
0x1001b048: push     esi
0x1001b049: push     esi
0x1001b04a: lea      edx, [esp + 0x7c]
0x1001b04e: push     0x102d040c ; "map/%s/%s_run.lua"
0x1001b053: push     edx
0x1001b054: call     0x10263225
0x1001b059: add      esp, 0x48
0x1001b05c: lea      eax, [esp + 0x3c]
0x1001b060: push     eax
0x1001b061: push     0x102d0420 ; "Load [%s]...\n"
0x1001b066: call     0x102647a4
0x1001b06b: lea      ecx, [esp + 0x44]
0x1001b06f: push     ecx
0x1001b070: call     0x10016ab0
0x1001b075: add      esp, 0xc
0x1001b078: jmp      0x1001b0a7
0x1001b07a: push     esi
0x1001b07b: push     esi
0x1001b07c: lea      edx, [esp + 0x44]
0x1001b080: push     0x102d0400 ; "map/%s/%s.o"
0x1001b085: push     edx
0x1001b086: call     0x10263225
0x1001b08b: lea      eax, [esp + 0x4c]
0x1001b08f: push     eax
0x1001b090: push     0x102d0420 ; "Load [%s]...\n"
0x1001b095: call     0x102647a4
0x1001b09a: lea      ecx, [esp + 0x54]
0x1001b09e: push     ecx
0x1001b09f: call     0x10016ab0
0x1001b0a4: add      esp, 0x1c
0x1001b0a7: push     0x102d03f0 ; "map_init...\n"
0x1001b0ac: call     0x102647a4
0x1001b0b1: push     0
0x1001b0b3: push     0
0x1001b0b5: push     0x102d03d8 ; "before script map_init"
0x1001b0ba: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"

### BeforeRunGameLogic_script_loader 0x1001afc5
0x1001afc5: push     ebp
0x1001afc6: jmp      0x1001b415
0x1001afcb: cmp      dword ptr [0x1036fcec], 0
0x1001afd2: je       0x1001b0a7
0x1001afd8: cmp      dword ptr [0x1036fcf0], 0
0x1001afdf: je       0x1001b07a ; "VV峊$Dh"
0x1001afe5: push     0x102d0480 ; "Load_Tab...\n"
0x1001afea: call     0x102647a4
0x1001afef: push     esi
0x1001aff0: push     0x102d047c
0x1001aff5: push     0x102d0470 ; "Load_Tab"
0x1001affa: call     0x100790b0
0x1001afff: mov      ecx, dword ptr [0x10589968]
0x1001b005: push     ecx
0x1001b006: push     0x102d0444 ; "[%d] 开始执行地图脚本, 读取物件和角色信息!\n"
0x1001b00b: push     0x102cea84 ; "init"
0x1001b010: call     0x10115fb0
0x1001b015: push     esi
0x1001b016: push     esi
0x1001b017: lea      edx, [esp + 0xac]
0x1001b01e: push     0x102d0430 ; "map/%s/%s_init.lua"
0x1001b023: push     edx
0x1001b024: call     0x10263225
0x1001b029: lea      eax, [esp + 0xb4]
0x1001b030: push     eax
0x1001b031: push     0x102d0420 ; "Load [%s]...\n"
0x1001b036: call     0x102647a4
0x1001b03b: lea      ecx, [esp + 0xbc]
0x1001b042: push     ecx
0x1001b043: call     0x10016ab0
0x1001b048: push     esi
0x1001b049: push     esi
0x1001b04a: lea      edx, [esp + 0x7c]
0x1001b04e: push     0x102d040c ; "map/%s/%s_run.lua"
0x1001b053: push     edx
0x1001b054: call     0x10263225
0x1001b059: add      esp, 0x48
0x1001b05c: lea      eax, [esp + 0x3c]
0x1001b060: push     eax
0x1001b061: push     0x102d0420 ; "Load [%s]...\n"
0x1001b066: call     0x102647a4
0x1001b06b: lea      ecx, [esp + 0x44]
0x1001b06f: push     ecx
0x1001b070: call     0x10016ab0
0x1001b075: add      esp, 0xc
0x1001b078: jmp      0x1001b0a7
0x1001b07a: push     esi
0x1001b07b: push     esi
0x1001b07c: lea      edx, [esp + 0x44]
0x1001b080: push     0x102d0400 ; "map/%s/%s.o"
0x1001b085: push     edx
0x1001b086: call     0x10263225
0x1001b08b: lea      eax, [esp + 0x4c]
0x1001b08f: push     eax
0x1001b090: push     0x102d0420 ; "Load [%s]...\n"
0x1001b095: call     0x102647a4
0x1001b09a: lea      ecx, [esp + 0x54]
0x1001b09e: push     ecx
0x1001b09f: call     0x10016ab0
0x1001b0a4: add      esp, 0x1c
0x1001b0a7: push     0x102d03f0 ; "map_init...\n"
0x1001b0ac: call     0x102647a4
0x1001b0b1: push     0
0x1001b0b3: push     0
0x1001b0b5: push     0x102d03d8 ; "before script map_init"
0x1001b0ba: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1001b0bf: push     0x10329d9a
0x1001b0c4: push     0x102d03cc ; "map_init"
0x1001b0c9: call     0x100790b0
0x1001b0ce: push     0
0x1001b0d0: push     0
0x1001b0d2: push     0x102d03b4 ; "after script map_init"
0x1001b0d7: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1001b0dc: mov      edx, dword ptr [0x10589968]
0x1001b0e2: push     edx
0x1001b0e3: push     0x102d039c ; "[%d] 成功执行map_init\n"
0x1001b0e8: push     0x102cea84 ; "init"
0x1001b0ed: call     0x10115fb0
0x1001b0f2: mov      eax, dword ptr [0x10377d08]
0x1001b0f7: push     0x102d038c ; "MaxPlayerNum"
0x1001b0fc: push     0xffffd8ee
0x1001b101: push     eax
0x1001b102: mov      ebp, 0xe
0x1001b107: call     0x101fd470
0x1001b10c: mov      ecx, dword ptr [0x10377d08]
0x1001b112: push     -1
0x1001b114: push     ecx
0x1001b115: call     0x101fce00
0x1001b11a: add      esp, 0x44
0x1001b11d: test     eax, eax
0x1001b11f: jne      0x1001b143
0x1001b121: push     0x102d0364 ; "msgMaxPlayerNum全局脚本变量没有找到!\n"
0x1001b126: push     0x102cead4 ; "error"
0x1001b12b: call     0x10115fb0
0x1001b130: mov      edx, dword ptr [0x10377d08]
0x1001b136: push     -2
0x1001b138: push     edx
0x1001b139: call     0x101fcba0
0x1001b13e: add      esp, 0x10
0x1001b141: jmp      0x1001b184
0x1001b143: mov      eax, dword ptr [0x10377d08]
0x1001b148: push     -1
0x1001b14a: push     eax
0x1001b14b: call     0x101fcf40
0x1001b150: add      esp, 8
0x1001b153: call     0x10263430
0x1001b158: mov      ebp, eax
0x1001b15a: cmp      ebp, 0x20
0x1001b15d: jle      0x1001b173
0x1001b15f: push     0x20
0x1001b161: push     0x102d0338 ; "msg脚本变量MaxPlayerNum超出程序约定的%d!\n"
0x1001b166: push     0x102cead4 ; "error"
0x1001b16b: call     0x10115fb0
0x1001b170: add      esp, 0xc
0x1001b173: mov      ecx, dword ptr [0x10377d08]
0x1001b179: push     -2
0x1001b17b: push     ecx
0x1001b17c: call     0x101fcba0
0x1001b181: add      esp, 8
0x1001b184: mov      edi, 1
0x1001b189: cmp      ebp, edi
0x1001b18b: jl       0x1001b25c
0x1001b191: push     edi
0x1001b192: lea      edx, [esp + 0x14c]
0x1001b199: push     0x102d0314 ; "tmp_side=CONTROL_PLAYER[%d].side"
0x1001b19e: push     edx
0x1001b19f: call     0x10263225
0x1001b1a4: lea      eax, [esp + 0x154]
0x1001b1ab: push     eax
0x1001b1ac: call     0x10079870
0x1001b1b1: mov      ecx, dword ptr [0x10377d08]
0x1001b1b7: push     0x102d0308 ; "tmp_side"
0x1001b1bc: push     0xffffd8ee
0x1001b1c1: push     ecx
0x1001b1c2: call     0x101fd470
0x1001b1c7: mov      edx, dword ptr [0x10377d08]
0x1001b1cd: push     -1
0x1001b1cf: push     edx
0x1001b1d0: call     0x101fce00
0x1001b1d5: add      esp, 0x24
0x1001b1d8: test     eax, eax
0x1001b1da: jne      0x1001b211
0x1001b1dc: push     0x102d02e4 ; "msgtmp_side全局脚本变量没有找到!\n"
0x1001b1e1: push     0x102cead4 ; "error"
0x1001b1e6: call     0x10115fb0
0x1001b1eb: add      esp, 8
0x1001b1ee: push     0x102d02c4 ; "tmp_side全局脚本变量没有找到!"
0x1001b1f3: push     2
0x1001b1f5: mov      ecx, 0x10383f30
0x1001b1fa: call     0x100f66f0
0x1001b1ff: mov      eax, dword ptr [0x10377d08]
0x1001b204: push     -2
0x1001b206: push     eax
0x1001b207: call     0x101fcba0
0x1001b20c: add      esp, 8
0x1001b20f: jmp      0x1001b251
0x1001b211: mov      ecx, dword ptr [0x10377d08]
0x1001b217: push     -1
0x1001b219: push     ecx
0x1001b21a: call     0x101fcf40
0x1001b21f: call     0x10263430
0x1001b224: mov      edx, dword ptr [0x10377d08]
0x1001b22a: push     -2
0x1001b22c: push     edx
0x1001b22d: mov      esi, eax
0x1001b22f: call     0x101fcba0
0x1001b234: add      esp, 0x10
0x1001b237: test     esi, esi
0x1001b239: jle      0x1001b23e
0x1001b23b: sub      esi, 1
0x1001b23e: mov      ecx, dword ptr [0x1036fdb0]
0x1001b244: push     esi
0x1001b245: push     edi
0x1001b246: add      ecx, 0x1ef8
0x1001b24c: call     0x100f4a30
0x1001b251: add      edi, 1
0x1001b254: cmp      edi, ebp
0x1001b256: jle      0x1001b191 ; "W崝$L"
0x1001b25c: mov      esi, 0x10
0x1001b261: push     esi
0x1001b262: push     0x102d02b0 ; "生成动态障碍信息"
0x1001b267: lea      ecx, [esp + 0x28]
0x1001b26b: mov      dword ptr [esp + 0x40], 0xf
0x1001b273: mov      dword ptr [esp + 0x3c], 0
0x1001b27b: mov      byte ptr [esp + 0x2c], 0
0x1001b280: call     0x100019e0
0x1001b285: cmp      dword ptr [esp + 0x38], esi
0x1001b289: mov      eax, dword ptr [esp + 0x24]
0x1001b28d: mov      dword ptr [esp + 0x254], 2
0x1001b298: jae      0x1001b29e
0x1001b29a: lea      eax, [esp + 0x24]
0x1001b29e: push     eax
0x1001b29f: push     0x50
0x1001b2a1: call     0x10077c20
0x1001b2a6: mov      eax, dword ptr [esp + 0x2c]
0x1001b2aa: add      esp, 8
0x1001b2ad: cmp      dword ptr [esp + 0x38], esi
0x1001b2b1: jae      0x1001b2b7
0x1001b2b3: lea      eax, [esp + 0x24]
0x1001b2b7: push     eax
0x1001b2b8: mov      eax, dword ptr [0x10589968]
0x1001b2bd: push     eax
0x1001b2be: push     0x102d02a0 ; "[%d] 下一步:%s\n"
0x1001b2c3: push     0x102cea84 ; "init"
0x1001b2c8: call     0x10115fb0
0x1001b2cd: mov      ecx, dword ptr [0x1036fca8]
0x1001b2d3: mov      edx, dword ptr [ecx + 8]
0x1001b2d6: add      esp, 0x10
0x1001b2d9: push     0
0x1001b2db: push     0x50
0x1001b2dd: push     0x1788
0x1001b2e2: push     edx
0x1001b2e3: call     dword ptr [0x102ce458]
0x1001b2e9: mov      eax, dword ptr [0x10585800]
0x1001b2ee: test     eax, eax
0x1001b2f0: je       0x1001b307
0x1001b2f2: cmp      dword ptr [esp + 0x38], esi
0x1001b2f6: mov      ecx, dword ptr [esp + 0x24]
0x1001b2fa: jae      0x1001b300 ; "Qj<j"
0x1001b2fc: lea      ecx, [esp + 0x24]
0x1001b300: push     ecx
0x1001b301: push     0x3c
0x1001b303: push     0
0x1001b305: call     eax
0x1001b307: cmp      dword ptr [esp + 0x38], esi
0x1001b30b: jb       0x1001b417
0x1001b311: mov      eax, dword ptr [esp + 0x24]
0x1001b315: push     eax
0x1001b316: call     0x100028e0
0x1001b31b: add      esp, 4
0x1001b31e: jmp      0x1001b417
0x1001b323: push     0x102d0298 ; "sanguo"
0x1001b328: call     0x1001a920
0x1001b32d: push     0x102d028c ; "特效预加载"
0x1001b332: push     0x5a
0x1001b334: call     0x10077c20
0x1001b339: add      esp, 8
0x1001b33c: jmp      0x1001b417
0x1001b341: call     0x10076c90
0x1001b346: mov      ecx, dword ptr [0x10589968]
0x1001b34c: push     ecx
0x1001b34d: push     0x102d026c ; "[%d] GameEvent_MapInit() ok!\n"
0x1001b352: push     0x102cea84 ; "init"
0x1001b357: call     0x10115fb0
0x1001b35c: mov      eax, dword ptr [0x1036fca8]
0x1001b361: lea      edx, [eax + 0x5f0]
0x1001b367: push     edx
0x1001b368: add      eax, 0x5b0
0x1001b36d: push     eax
0x1001b36e: lea      eax, [esp + 0xdc]
0x1001b375: push     0x102d0254 ; "load_rolesdk(%s, "%s")"
0x1001b37a: push     eax
0x1001b37b: call     0x10263225
0x1001b380: lea      ecx, [esp + 0xe4]
0x1001b387: push     ecx
0x1001b388: call     0x10079870
0x1001b38d: mov      ecx, dword ptr [0x1036fdb0]
0x1001b393: add      esp, 0x20
0x1001b396: call     0x10071820
0x1001b39b: push     0
0x1001b39d: push     0
0x1001b39f: push     0x102d0240 ; "after init NodeMgr"
0x1001b3a4: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1001b3a9: push     0x102d0234 ; "加载成功"
0x1001b3ae: push     0x64
0x1001b3b0: call     0x10077c20
0x1001b3b5: mov      edx, dword ptr [0x1036fca8]
0x1001b3bb: mov      eax, dword ptr [edx + 8]
0x1001b3be: add      esp, 0x14
0x1001b3c1: push     0
0x1001b3c3: push     0x64
0x1001b3c5: push     0x1788
0x1001b3ca: push     eax
0x1001b3cb: call     dword ptr [0x102ce458]
0x1001b3d1: mov      eax, dword ptr [0x10585800]
0x1001b3d6: test     eax, eax
0x1001b3d8: je       0x1001b417
0x1001b3da: push     0x102d0234 ; "加载成功"
0x1001b3df: push     0x46
0x1001b3e1: jmp      0x1001b413
0x1001b3e3: call     0x10076c60
0x1001b3e8: push     0
0x1001b3ea: push     0
0x1001b3ec: push     0x102d021c ; "after loadmap ok event"
0x1001b3f1: mov      dword ptr [edi + 0x7a4], 1
0x1001b3fb: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1001b400: mov      eax, dword ptr [0x10585800]
0x1001b405: add      esp, 0xc
0x1001b408: test     eax, eax
0x1001b40a: je       0x1001b417
0x1001b40c: push     0x102d0210 ; "加载完成"
0x1001b411: push     0x6e
0x1001b413: push     0
0x1001b415: call     eax
0x1001b417: mov      eax, 1
0x1001b41c: mov      ecx, dword ptr [esp + 0x24c]
0x1001b423: mov      dword ptr fs:[0], ecx
0x1001b42a: pop      ecx
0x1001b42b: pop      edi
0x1001b42c: pop      esi
0x1001b42d: pop      ebp
0x1001b42e: mov      ecx, dword ptr [esp + 0x238]
0x1001b435: xor      ecx, esp
0x1001b437: call     0x10261f90
0x1001b43c: add      esp, 0x248
0x1001b442: ret      8
0x1001b445: lea      ecx, [ecx]
0x1001b448: retf     0x1ac
0x1001b44b: adc      byte ptr [ecx - 0x53], ah
0x1001b44e: add      dword ptr [eax], edx
0x1001b450: adc      al, 0xaf
0x1001b452: add      dword ptr [eax], edx
0x1001b454: retf     
0x1001b455: scasd    eax, dword ptr es:[edi]
0x1001b456: add      dword ptr [eax], edx
0x1001b458: and      esi, dword ptr [ebx - 0x4cbeefff]
0x1001b45e: add      dword ptr [eax], edx
0x1001b460: jecxz    0x1001b415
0x1001b462: add      dword ptr [eax], edx
0x1001b464: int3     
0x1001b465: int3     
0x1001b466: int3     
0x1001b467: int3     
0x1001b468: int3     
0x1001b469: int3     
0x1001b46a: int3     
0x1001b46b: int3     
0x1001b46c: int3     
0x1001b46d: int3     
0x1001b46e: int3     
0x1001b46f: int3     
0x1001b470: mov      eax, dword ptr [esp + 0x10]
0x1001b474: push     ebx
0x1001b475: push     esi
0x1001b476: mov      esi, ecx
0x1001b478: mov      edx, dword ptr [esi + 4]
0x1001b47b: test     edx, edx
0x1001b47d: mov      ecx, dword ptr [eax]
0x1001b47f: mov      dword ptr [esp + 0x18], ecx
0x1001b483: jne      0x1001b489
0x1001b485: xor      eax, eax
0x1001b487: jmp      0x1001b491
0x1001b489: mov      eax, dword ptr [esi + 0xc]
0x1001b48c: sub      eax, edx
0x1001b48e: sar      eax, 2
0x1001b491: mov      ebx, dword ptr [esp + 0x14]
0x1001b495: test     ebx, ebx
0x1001b497: je       0x1001b625
0x1001b49d: test     edx, edx
0x1001b49f: jne      0x1001b4a5
0x1001b4a1: xor      ecx, ecx
0x1001b4a3: jmp      0x1001b4ad
0x1001b4a5: mov      ecx, dword ptr [esi + 8]
0x1001b4a8: sub      ecx, edx
0x1001b4aa: sar      ecx, 2
0x1001b4ad: push     edi
0x1001b4ae: mov      edi, 0x3fffffff
0x1001b4b3: sub      edi, ecx
0x1001b4b5: cmp      edi, ebx
0x1001b4b7: jae      0x1001b4be
0x1001b4b9: call     0x10012370
0x1001b4be: test     edx, edx
0x1001b4c0: jne      0x1001b4c6
0x1001b4c2: xor      ecx, ecx
0x1001b4c4: jmp      0x1001b4ce
0x1001b4c6: mov      ecx, dword ptr [esi + 8]
0x1001b4c9: sub      ecx, edx
0x1001b4cb: sar      ecx, 2
0x1001b4ce: add      ecx, ebx
0x1001b4d0: cmp      eax, ecx
0x1001b4d2: push     ebp
0x1001b4d3: jae      0x1001b592
0x1001b4d9: mov      ecx, eax
0x1001b4db: shr      ecx, 1
0x1001b4dd: mov      edi, 0x3fffffff
0x1001b4e2: sub      edi, ecx
0x1001b4e4: cmp      edi, eax
0x1001b4e6: jae      0x1001b4ec
0x1001b4e8: xor      eax, eax
0x1001b4ea: jmp      0x1001b4ee
0x1001b4ec: add      eax, ecx
0x1001b4ee: test     edx, edx
0x1001b4f0: jne      0x1001b4f6
0x1001b4f2: xor      ecx, ecx
0x1001b4f4: jmp      0x1001b4fe
0x1001b4f6: mov      ecx, dword ptr [esi + 8]
0x1001b4f9: sub      ecx, edx
0x1001b4fb: sar      ecx, 2
0x1001b4fe: add      ecx, ebx
0x1001b500: cmp      eax, ecx
0x1001b502: jae      0x1001b516
0x1001b504: test     edx, edx
0x1001b506: jne      0x1001b50c
0x1001b508: xor      eax, eax
0x1001b50a: jmp      0x1001b514
0x1001b50c: mov      eax, dword ptr [esi + 8]
0x1001b50f: sub      eax, edx
0x1001b511: sar      eax, 2
0x1001b514: add      eax, ebx
0x1001b516: add      eax, eax
0x1001b518: add      eax, eax
0x1001b51a: push     0x1a
0x1001b51c: push     eax
0x1001b51d: mov      dword ptr [esp + 0x24], eax
0x1001b521: call     0x10002810 ; "V媡$兤V鑇{&"
0x1001b526: mov      ebp, dword ptr [esp + 0x20]
0x1001b52a: mov      edx, dword ptr [esi + 4]
0x1001b52d: add      esp, 8
0x1001b530: mov      edi, eax
0x1001b532: push     edi
0x1001b533: push     ebp
0x1001b534: push     edx
0x1001b535: mov      ecx, esi
0x1001b537: call     0x10019990
0x1001b53c: lea      ecx, [esp + 0x20]
0x1001b540: push     ecx
0x1001b541: push     ebx
0x1001b542: push     eax
0x1001b543: mov      ecx, esi
0x1001b545: call     0x10019c00
0x1001b54a: mov      edx, dword ptr [esi + 8]
0x1001b54d: push     eax
0x1001b54e: push     edx
0x1001b54f: push     ebp
0x1001b550: mov      ecx, esi
0x1001b552: call     0x10019990
0x1001b557: mov      eax, dword ptr [esi + 4]
0x1001b55a: test     eax, eax
0x1001b55c: jne      0x1001b562
0x1001b55e: xor      ecx, ecx
0x1001b560: jmp      0x1001b56a
0x1001b562: mov      ecx, dword ptr [esi + 8]
0x1001b565: sub      ecx, eax
0x1001b567: sar      ecx, 2
0x1001b56a: add      ebx, ecx
0x1001b56c: test     eax, eax
0x1001b56e: je       0x1001b579
0x1001b570: push     eax
0x1001b571: call     0x100028e0
0x1001b576: add      esp, 4
0x1001b579: mov      eax, dword ptr [esp + 0x1c]
0x1001b57d: pop      ebp
0x1001b57e: lea      ecx, [edi + ebx*4]
0x1001b581: add      eax, edi
0x1001b583: mov      dword ptr [esi + 4], edi
0x1001b586: pop      edi
0x1001b587: mov      dword ptr [esi + 0xc], eax
0x1001b58a: mov      dword ptr [esi + 8], ecx
0x1001b58d: pop      esi
0x1001b58e: pop      ebx
0x1001b58f: ret      0x10
0x1001b592: mov      ebp, dword ptr [esi + 8]
0x1001b595: mov      edi, dword ptr [esp + 0x18]
0x1001b599: mov      edx, ebp
0x1001b59b: sub      edx, edi
0x1001b59d: sar      edx, 2
0x1001b5a0: cmp      edx, ebx
0x1001b5a2: lea      eax, [ebx*4]
0x1001b5a9: mov      ecx, esi
0x1001b5ab: mov      dword ptr [esp + 0x1c], eax
0x1001b5af: jae      0x1001b5f7
0x1001b5b1: add      eax, edi
0x1001b5b3: push     eax
0x1001b5b4: push     ebp
0x1001b5b5: push     edi
0x1001b5b6: call     0x10019990
0x1001b5bb: mov      eax, dword ptr [esi + 8]
0x1001b5be: mov      edx, eax
0x1001b5c0: sub      edx, edi
0x1001b5c2: lea      ecx, [esp + 0x20]
0x1001b5c6: push     ecx
0x1001b5c7: sar      edx, 2
0x1001b5ca: sub      ebx, edx
0x1001b5cc: push     ebx
0x1001b5cd: push     eax
0x1001b5ce: mov      ecx, esi
0x1001b5d0: call     0x10019c00
0x1001b5d5: mov      eax, dword ptr [esp + 0x1c]
0x1001b5d9: add      dword ptr [esi + 8], eax
0x1001b5dc: mov      esi, dword ptr [esi + 8]
0x1001b5df: lea      ecx, [esp + 0x20]
0x1001b5e3: push     ecx
0x1001b5e4: sub      esi, eax
0x1001b5e6: push     esi
0x1001b5e7: push     edi
0x1001b5e8: call     0x100190a0
0x1001b5ed: add      esp, 0xc
0x1001b5f0: pop      ebp
0x1001b5f1: pop      edi
0x1001b5f2: pop      esi
0x1001b5f3: pop      ebx
0x1001b5f4: ret      0x10
0x1001b5f7: push     ebp
0x1001b5f8: mov      ebx, ebp
0x1001b5fa: sub      ebx, eax
0x1001b5fc: push     ebp
0x1001b5fd: push     ebx
0x1001b5fe: call     0x10019990
0x1001b603: push     ebp
0x1001b604: push     ebx
0x1001b605: push     edi
0x1001b606: mov      dword ptr [esi + 8], eax
0x1001b609: call     0x100190c0
0x1001b60e: mov      eax, dword ptr [esp + 0x28]
0x1001b612: lea      edx, [esp + 0x2c]
0x1001b616: push     edx
0x1001b617: add      eax, edi
0x1001b619: push     eax
0x1001b61a: push     edi
0x1001b61b: call     0x100190a0
0x1001b620: add      esp, 0x18
0x1001b623: pop      ebp
0x1001b624: pop      edi
0x1001b625: pop      esi
0x1001b626: pop      ebx
0x1001b627: ret      0x10
0x1001b62a: int3     
0x1001b62b: int3     
0x1001b62c: int3     
0x1001b62d: int3     
0x1001b62e: int3     
0x1001b62f: int3     
0x1001b630: mov      eax, dword ptr [esp + 0x10]
0x1001b634: push     ebx
0x1001b635: push     esi
0x1001b636: mov      esi, ecx
0x1001b638: mov      edx, dword ptr [esi + 4]
0x1001b63b: test     edx, edx
0x1001b63d: mov      ecx, dword ptr [eax]
0x1001b63f: mov      dword ptr [esp + 0x18], ecx
0x1001b643: jne      0x1001b649
0x1001b645: xor      eax, eax
0x1001b647: jmp      0x1001b651
0x1001b649: mov      eax, dword ptr [esi + 0xc]
0x1001b64c: sub      eax, edx
0x1001b64e: sar      eax, 2
0x1001b651: mov      ebx, dword ptr [esp + 0x14]
0x1001b655: test     ebx, ebx
0x1001b657: je       0x1001b7e5
0x1001b65d: test     edx, edx
0x1001b65f: jne      0x1001b665
0x1001b661: xor      ecx, ecx
0x1001b663: jmp      0x1001b66d
0x1001b665: mov      ecx, dword ptr [esi + 8]
0x1001b668: sub      ecx, edx
0x1001b66a: sar      ecx, 2
0x1001b66d: push     edi
0x1001b66e: mov      edi, 0x3fffffff
0x1001b673: sub      edi, ecx
0x1001b675: cmp      edi, ebx
0x1001b677: jae      0x1001b67e
0x1001b679: call     0x100123f0
0x1001b67e: test     edx, edx
0x1001b680: jne      0x1001b686
0x1001b682: xor      ecx, ecx
0x1001b684: jmp      0x1001b68e
0x1001b686: mov      ecx, dword ptr [esi + 8]
0x1001b689: sub      ecx, edx
0x1001b68b: sar      ecx, 2
0x1001b68e: add      ecx, ebx
0x1001b690: cmp      eax, ecx
0x1001b692: push     ebp
0x1001b693: jae      0x1001b752
0x1001b699: mov      ecx, eax
0x1001b69b: shr      ecx, 1
0x1001b69d: mov      edi, 0x3fffffff
0x1001b6a2: sub      edi, ecx
0x1001b6a4: cmp      edi, eax
0x1001b6a6: jae      0x1001b6ac
0x1001b6a8: xor      eax, eax
0x1001b6aa: jmp      0x1001b6ae
0x1001b6ac: add      eax, ecx
0x1001b6ae: test     edx, edx
0x1001b6b0: jne      0x1001b6b6
0x1001b6b2: xor      ecx, ecx
0x1001b6b4: jmp      0x1001b6be
0x1001b6b6: mov      ecx, dword ptr [esi + 8]
0x1001b6b9: sub      ecx, edx
0x1001b6bb: sar      ecx, 2
0x1001b6be: add      ecx, ebx
0x1001b6c0: cmp      eax, ecx
0x1001b6c2: jae      0x1001b6d6
0x1001b6c4: test     edx, edx
0x1001b6c6: jne      0x1001b6cc
0x1001b6c8: xor      eax, eax
0x1001b6ca: jmp      0x1001b6d4
0x1001b6cc: mov      eax, dword ptr [esi + 8]
0x1001b6cf: sub      eax, edx
0x1001b6d1: sar      eax, 2
0x1001b6d4: add      eax, ebx
0x1001b6d6: add      eax, eax
0x1001b6d8: add      eax, eax
0x1001b6da: push     0x1a
0x1001b6dc: push     eax
0x1001b6dd: mov      dword ptr [esp + 0x24], eax
0x1001b6e1: call     0x10002810 ; "V媡$兤V鑇{&"
0x1001b6e6: mov      ebp, dword ptr [esp + 0x20]
0x1001b6ea: mov      edx, dword ptr [esi + 4]
0x1001b6ed: add      esp, 8
0x1001b6f0: mov      edi, eax
0x1001b6f2: push     edi
0x1001b6f3: push     ebp
0x1001b6f4: push     edx
0x1001b6f5: mov      ecx, esi
0x1001b6f7: call     0x100199c0
0x1001b6fc: lea      ecx, [esp + 0x20]
0x1001b700: push     ecx
0x1001b701: push     ebx
0x1001b702: push     eax
0x1001b703: mov      ecx, esi
0x1001b705: call     0x10019c30
0x1001b70a: mov      edx, dword ptr [esi + 8]
0x1001b70d: push     eax
0x1001b70e: push     edx
0x1001b70f: push     ebp
0x1001b710: mov      ecx, esi
0x1001b712: call     0x100199c0
0x1001b717: mov      eax, dword ptr [esi + 4]
0x1001b71a: test     eax, eax
0x1001b71c: jne      0x1001b722
0x1001b71e: xor      ecx, ecx
0x1001b720: jmp      0x1001b72a
0x1001b722: mov      ecx, dword ptr [esi + 8]
0x1001b725: sub      ecx, eax
0x1001b727: sar      ecx, 2
0x1001b72a: add      ebx, ecx
0x1001b72c: test     eax, eax
0x1001b72e: je       0x1001b739
0x1001b730: push     eax
0x1001b731: call     0x100028e0
0x1001b736: add      esp, 4
0x1001b739: mov      eax, dword ptr [esp + 0x1c]
0x1001b73d: pop      ebp
0x1001b73e: lea      ecx, [edi + ebx*4]
0x1001b741: add      eax, edi
0x1001b743: mov      dword ptr [esi + 4], edi
0x1001b746: pop      edi
0x1001b747: mov      dword ptr [esi + 0xc], eax
0x1001b74a: mov      dword ptr [esi + 8], ecx
0x1001b74d: pop      esi
0x1001b74e: pop      ebx
0x1001b74f: ret      0x10
0x1001b752: mov      ebp, dword ptr [esi + 8]
0x1001b755: mov      edi, dword ptr [esp + 0x18]
0x1001b759: mov      edx, ebp
0x1001b75b: sub      edx, edi
0x1001b75d: sar      edx, 2
0x1001b760: cmp      edx, ebx
0x1001b762: lea      eax, [ebx*4]
0x1001b769: mov      ecx, esi
0x1001b76b: mov      dword ptr [esp + 0x1c], eax
0x1001b76f: jae      0x1001b7b7
0x1001b771: add      eax, edi
0x1001b773: push     eax
0x1001b774: push     ebp
0x1001b775: push     edi
0x1001b776: call     0x100199c0
0x1001b77b: mov      eax, dword ptr [esi + 8]
0x1001b77e: mov      edx, eax
0x1001b780: sub      edx, edi
0x1001b782: lea      ecx, [esp + 0x20]
0x1001b786: push     ecx
0x1001b787: sar      edx, 2
0x1001b78a: sub      ebx, edx
0x1001b78c: push     ebx
0x1001b78d: push     eax
0x1001b78e: mov      ecx, esi
0x1001b790: call     0x10019c30
0x1001b795: mov      eax, dword ptr [esp + 0x1c]
0x1001b799: add      dword ptr [esi + 8], eax
0x1001b79c: mov      esi, dword ptr [esi + 8]
0x1001b79f: lea      ecx, [esp + 0x20]
0x1001b7a3: push     ecx
0x1001b7a4: sub      esi, eax
0x1001b7a6: push     esi
0x1001b7a7: push     edi
0x1001b7a8: call     0x100190f0
0x1001b7ad: add      esp, 0xc
0x1001b7b0: pop      ebp
0x1001b7b1: pop      edi
0x1001b7b2: pop      esi
0x1001b7b3: pop      ebx
0x1001b7b4: ret      0x10
0x1001b7b7: push     ebp
0x1001b7b8: mov      ebx, ebp
0x1001b7ba: sub      ebx, eax
0x1001b7bc: push     ebp
0x1001b7bd: push     ebx
0x1001b7be: call     0x100199c0
0x1001b7c3: push     ebp
0x1001b7c4: push     ebx

### DoFile_or_LoadLua? 0x10016ab0
0x10016ab0: mov      eax, dword ptr [0x10377d08]
0x10016ab5: push     esi
0x10016ab6: mov      esi, dword ptr [esp + 8]
0x10016aba: push     esi
0x10016abb: push     eax
0x10016abc: call     0x101fc6f0 ; "婦$V媡$WPV鑿4"
0x10016ac1: add      esp, 8
0x10016ac4: test     eax, eax
0x10016ac6: push     esi
0x10016ac7: je       0x10016adf
0x10016ac9: push     0x102cf9e8 ; "do file fail![%s]\n"
0x10016ace: push     0x102cead4 ; "error"
0x10016ad3: call     0x10115fb0
0x10016ad8: add      esp, 0xc
0x10016adb: xor      eax, eax
0x10016add: pop      esi
0x10016ade: ret      
0x10016adf: push     0x102cf9d8 ; "do [%s] ok!\n"
0x10016ae4: push     0x102cea84 ; "init"
0x10016ae9: call     0x10115fb0
0x10016aee: add      esp, 0xc
0x10016af1: mov      eax, 1
0x10016af6: pop      esi
0x10016af7: ret      
0x10016af8: int3     
0x10016af9: int3     
0x10016afa: int3     
0x10016afb: int3     
0x10016afc: int3     
0x10016afd: int3     
0x10016afe: int3     
0x10016aff: int3     
0x10016b00: mov      byte ptr [ecx + 0xc85], 1
0x10016b07: ret      
0x10016b08: int3     
0x10016b09: int3     
0x10016b0a: int3     
0x10016b0b: int3     
0x10016b0c: int3     
0x10016b0d: int3     
0x10016b0e: int3     
0x10016b0f: int3     
0x10016b10: mov      al, byte ptr [ecx + 0xc85]
0x10016b16: ret      
0x10016b17: int3     
0x10016b18: int3     
0x10016b19: int3     
0x10016b1a: int3     
0x10016b1b: int3     
0x10016b1c: int3     
0x10016b1d: int3     
0x10016b1e: int3     
0x10016b1f: int3     
0x10016b20: mov      al, byte ptr [esp + 4]
0x10016b24: mov      byte ptr [ecx + 0xc86], al
0x10016b2a: ret      4
0x10016b2d: int3     
0x10016b2e: int3     
0x10016b2f: int3     
0x10016b30: mov      al, byte ptr [ecx + 0xc86]
0x10016b36: ret      
0x10016b37: int3     
0x10016b38: int3     
0x10016b39: int3     
0x10016b3a: int3     
0x10016b3b: int3     
0x10016b3c: int3     
0x10016b3d: int3     
0x10016b3e: int3     
0x10016b3f: int3     
0x10016b40: call     0x10077640
0x10016b45: push     0
0x10016b47: push     0
0x10016b49: push     0x102cfa18 ; "after StartRun"
0x10016b4e: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x10016b53: add      esp, 0xc
0x10016b56: ret      
0x10016b57: int3     
0x10016b58: int3     
0x10016b59: int3     
0x10016b5a: int3     
0x10016b5b: int3     
0x10016b5c: int3     
0x10016b5d: int3     
0x10016b5e: int3     
0x10016b5f: int3     
0x10016b60: fld      dword ptr [0x102cfa28]
0x10016b66: push     ecx
0x10016b67: mov      ecx, dword ptr [ecx + 0x7b8]
0x10016b6d: fstp     dword ptr [esp]
0x10016b70: call     0x100e84b0 ; "儁t"
0x10016b75: ret      
0x10016b76: int3     
0x10016b77: int3     
0x10016b78: int3     
0x10016b79: int3     
0x10016b7a: int3     
0x10016b7b: int3     
0x10016b7c: int3     
0x10016b7d: int3     
0x10016b7e: int3     
0x10016b7f: int3     
0x10016b80: mov      eax, 1
0x10016b85: ret      
0x10016b86: int3     
0x10016b87: int3     
0x10016b88: int3     
0x10016b89: int3     
0x10016b8a: int3     
0x10016b8b: int3     
0x10016b8c: int3     
0x10016b8d: int3     
0x10016b8e: int3     
0x10016b8f: int3     
0x10016b90: sub      esp, 0x24
0x10016b93: mov      eax, dword ptr [0x10367584]
0x10016b98: xor      eax, esp
0x10016b9a: mov      dword ptr [esp + 0x20], eax
0x10016b9e: mov      ecx, dword ptr [esp + 0x30]
0x10016ba2: push     esi
0x10016ba3: mov      esi, dword ptr [esp + 0x2c]
0x10016ba7: lea      eax, [esp + 0x38]
0x10016bab: push     eax
0x10016bac: push     ecx
0x10016bad: push     0x10370178
0x10016bb2: call     0x10263dc5
0x10016bb7: mov      edx, dword ptr [0x1036fca8]
0x10016bbd: movsx    eax, byte ptr [edx + 0x7d1]
0x10016bc4: push     eax
0x10016bc5: push     esi
0x10016bc6: lea      ecx, [esp + 0x18]
0x10016bca: push     0x102cfa40 ; "%s_%d"
0x10016bcf: push     ecx
0x10016bd0: call     0x10263225
0x10016bd5: add      esp, 0x1c
0x10016bd8: cmp      dword ptr [esp + 0x30], 0
0x10016bdd: pop      esi
0x10016bde: push     0x10370178
0x10016be3: je       0x10016bf8
0x10016be5: mov      edx, dword ptr [0x10589968]
0x10016beb: push     edx
0x10016bec: push     0x102cfa34 ; "msg%d:%s"
0x10016bf1: lea      eax, [esp + 0xc]
0x10016bf5: push     eax
0x10016bf6: jmp      0x10016c09
0x10016bf8: mov      ecx, dword ptr [0x10589968]
0x10016bfe: push     ecx
0x10016bff: push     0x102cfa2c ; "%d:%s"
0x10016c04: lea      edx, [esp + 0xc]
0x10016c08: push     edx
0x10016c09: call     0x10115fb0
0x10016c0e: mov      ecx, dword ptr [esp + 0x30]
0x10016c12: add      esp, 0x10
0x10016c15: xor      ecx, esp
0x10016c17: call     0x10261f90
0x10016c1c: add      esp, 0x24
0x10016c1f: ret      
0x10016c20: sub      esp, 0x24
0x10016c23: mov      eax, dword ptr [0x10367584]
0x10016c28: xor      eax, esp
0x10016c2a: mov      dword ptr [esp + 0x20], eax
0x10016c2e: cmp      dword ptr [0x10370170], 0
0x10016c35: push     esi
0x10016c36: mov      esi, dword ptr [esp + 0x2c]
0x10016c3a: jle      0x10016c8c ; "婰$$^3惕$"
0x10016c3c: mov      ecx, dword ptr [esp + 0x30]
0x10016c40: lea      eax, [esp + 0x34]
0x10016c44: push     eax
0x10016c45: push     ecx
0x10016c46: push     0x10370978
0x10016c4b: call     0x10263dc5
0x10016c50: mov      edx, dword ptr [0x1036fca8]
0x10016c56: movsx    eax, byte ptr [edx + 0x7d1]
0x10016c5d: push     eax
0x10016c5e: push     esi
0x10016c5f: lea      ecx, [esp + 0x18]
0x10016c63: push     0x102cfa40 ; "%s_%d"
0x10016c68: push     ecx
0x10016c69: call     0x10263225
0x10016c6e: mov      edx, dword ptr [0x10589968]
0x10016c74: push     0x10370978
0x10016c79: push     edx
0x10016c7a: lea      eax, [esp + 0x28]
0x10016c7e: push     0x102cfa2c ; "%d:%s"
0x10016c83: push     eax
0x10016c84: call     0x10115fb0
0x10016c89: add      esp, 0x2c
0x10016c8c: mov      ecx, dword ptr [esp + 0x24]
0x10016c90: pop      esi
0x10016c91: xor      ecx, esp
0x10016c93: call     0x10261f90
0x10016c98: add      esp, 0x24
0x10016c9b: ret      
0x10016c9c: int3     
0x10016c9d: int3     
0x10016c9e: int3     
0x10016c9f: int3     
0x10016ca0: ret      
0x10016ca1: int3     
0x10016ca2: int3     
0x10016ca3: int3     
0x10016ca4: int3     
0x10016ca5: int3     
0x10016ca6: int3     
0x10016ca7: int3     
0x10016ca8: int3     
0x10016ca9: int3     
0x10016caa: int3     
0x10016cab: int3     
0x10016cac: int3     
0x10016cad: int3     
0x10016cae: int3     
0x10016caf: int3     
0x10016cb0: mov      eax, dword ptr [esp + 4]
0x10016cb4: push     esi
0x10016cb5: mov      esi, ecx
0x10016cb7: mov      dword ptr [esi + 0x7f4], eax
0x10016cbd: call     dword ptr [0x102ce2d0]
0x10016cc3: mov      ecx, dword ptr [esi + 0x688]
0x10016cc9: imul     ecx, dword ptr [esi + 0x7f4]
0x10016cd0: sub      eax, ecx
0x10016cd2: mov      dword ptr [0x10370168], eax
0x10016cd7: pop      esi
0x10016cd8: ret      4
0x10016cdb: int3     
0x10016cdc: int3     
0x10016cdd: int3     
0x10016cde: int3     
0x10016cdf: int3     
0x10016ce0: mov      eax, dword ptr [esp + 4]
0x10016ce4: mov      edx, dword ptr [esp + 8]
0x10016ce8: mov      dword ptr [ecx + 0x850], eax
0x10016cee: mov      dword ptr [ecx + 0x858], eax
0x10016cf4: mov      eax, dword ptr [esp + 0xc]
0x10016cf8: mov      dword ptr [ecx + 0x854], edx

### lua_getglobal? wrapper 0x10079870
0x10079870: mov      eax, dword ptr [esp + 4]
0x10079874: mov      ecx, dword ptr [0x10377d08]
0x1007987a: push     eax
0x1007987b: push     ecx
0x1007987c: call     0x101fc780
0x10079881: add      esp, 8
0x10079884: ret      
0x10079885: int3     
0x10079886: int3     
0x10079887: int3     
0x10079888: int3     
0x10079889: int3     
0x1007988a: int3     
0x1007988b: int3     
0x1007988c: int3     
0x1007988d: int3     
0x1007988e: int3     
0x1007988f: int3     
0x10079890: mov      eax, dword ptr [esp + 4]
0x10079894: mov      ecx, dword ptr [esp + 8]
0x10079898: mov      dword ptr [eax], 0x10360170
0x1007989e: mov      dword ptr [ecx], 0x10360170
0x100798a4: ret      
0x100798a5: int3     
0x100798a6: int3     
0x100798a7: int3     
0x100798a8: int3     
0x100798a9: int3     
0x100798aa: int3     
0x100798ab: int3     
0x100798ac: int3     
0x100798ad: int3     
0x100798ae: int3     
0x100798af: int3     
0x100798b0: mov      edx, dword ptr [ecx + 0xc]
0x100798b3: lea      eax, [edx + 8]
0x100798b6: cmp      eax, dword ptr [ecx + 4]
0x100798b9: ja       0x100798e3
0x100798bb: mov      eax, dword ptr [ecx]
0x100798bd: add      eax, edx
0x100798bf: mov      edx, dword ptr [esp + 4]
0x100798c3: push     esi
0x100798c4: mov      esi, dword ptr [edx]
0x100798c6: mov      dword ptr [eax], esi
0x100798c8: mov      edx, dword ptr [edx + 4]
0x100798cb: mov      dword ptr [eax + 4], edx
0x100798ce: add      dword ptr [ecx + 0xc], 8
0x100798d2: mov      eax, dword ptr [ecx + 0xc]
0x100798d5: cmp      eax, dword ptr [ecx + 8]
0x100798d8: pop      esi
0x100798d9: jbe      0x100798de
0x100798db: mov      dword ptr [ecx + 8], eax
0x100798de: mov      al, 1
0x100798e0: ret      4
0x100798e3: xor      al, al
0x100798e5: ret      4
0x100798e8: int3     
0x100798e9: int3     
0x100798ea: int3     
0x100798eb: int3     
0x100798ec: int3     
0x100798ed: int3     
0x100798ee: int3     
0x100798ef: int3     
0x100798f0: mov      edx, dword ptr [ecx + 0xc]
0x100798f3: lea      eax, [edx + 0xe]
0x100798f6: cmp      eax, dword ptr [ecx + 4]
0x100798f9: ja       0x10079931
0x100798fb: mov      eax, dword ptr [ecx]
0x100798fd: add      eax, edx
0x100798ff: mov      edx, dword ptr [esp + 4]
0x10079903: push     esi
0x10079904: mov      esi, dword ptr [edx]
0x10079906: mov      dword ptr [eax], esi
0x10079908: mov      esi, dword ptr [edx + 4]
0x1007990b: mov      dword ptr [eax + 4], esi
0x1007990e: mov      esi, dword ptr [edx + 8]
0x10079911: mov      dword ptr [eax + 8], esi
0x10079914: mov      dx, word ptr [edx + 0xc]
0x10079918: mov      word ptr [eax + 0xc], dx
0x1007991c: add      dword ptr [ecx + 0xc], 0xe
0x10079920: mov      eax, dword ptr [ecx + 0xc]
0x10079923: cmp      eax, dword ptr [ecx + 8]
0x10079926: pop      esi
0x10079927: jbe      0x1007992c
0x10079929: mov      dword ptr [ecx + 8], eax
0x1007992c: mov      al, 1
0x1007992e: ret      4
0x10079931: xor      al, al
0x10079933: ret      4
0x10079936: int3     
0x10079937: int3     
0x10079938: int3     
0x10079939: int3     
0x1007993a: int3     
0x1007993b: int3     
0x1007993c: int3     
0x1007993d: int3     
0x1007993e: int3     
0x1007993f: int3     
0x10079940: push     esi
0x10079941: mov      esi, ecx
0x10079943: mov      ecx, dword ptr [esi + 0xc10]
0x10079949: test     ecx, ecx
0x1007994b: push     edi
0x1007994c: mov      edi, dword ptr [esp + 0xc]
0x10079950: je       0x10079961
0x10079952: mov      eax, dword ptr [esi + 0xc14]
0x10079958: sub      eax, ecx
0x1007995a: sar      eax, 2
0x1007995d: cmp      edi, eax
0x1007995f: jb       0x10079974
0x10079961: call     0x10261b2b
0x10079966: mov      eax, dword ptr [esi + 0xc10]
0x1007996c: mov      eax, dword ptr [eax + edi*4]
0x1007996f: pop      edi
0x10079970: pop      esi
0x10079971: ret      4
0x10079974: mov      eax, dword ptr [ecx + edi*4]
0x10079977: pop      edi
0x10079978: pop      esi
0x10079979: ret      4
0x1007997c: int3     
0x1007997d: int3     
0x1007997e: int3     
0x1007997f: int3     
0x10079980: mov      eax, dword ptr [0x1036fdb0]
0x10079985: mov      eax, dword ptr [eax + 0x1aac]
0x1007998b: test     eax, eax
0x1007998d: je       0x10079999
0x1007998f: mov      dword ptr [eax + 0xfe0], 1
0x10079999: xor      eax, eax
0x1007999b: ret      
0x1007999c: int3     
0x1007999d: int3     
0x1007999e: int3     
0x1007999f: int3     
