
### CGameScene_LoadMap 0x10070370
0x10070370: push     -1
0x10070372: push     0x102b2288 ; "T$ÿÿÿ"
0x10070377: mov      eax, dword ptr fs:[0]
0x1007037d: push     eax
0x1007037e: sub      esp, 0xec
0x10070384: mov      eax, dword ptr [0x10367584]
0x10070389: xor      eax, esp
0x1007038b: mov      dword ptr [esp + 0xe8], eax
0x10070392: push     ebx
0x10070393: push     ebp
0x10070394: push     esi
0x10070395: push     edi
0x10070396: mov      eax, dword ptr [0x10367584]
0x1007039b: xor      eax, esp
0x1007039d: push     eax
0x1007039e: lea      eax, [esp + 0x100]
0x100703a5: mov      dword ptr fs:[0], eax
0x100703ab: mov      edi, dword ptr [esp + 0x110]
0x100703b2: xor      ebx, ebx
0x100703b4: push     ebx
0x100703b5: push     ebx
0x100703b6: push     0x102d6860 ; "Scene LoadMap Begin"
0x100703bb: mov      esi, ecx
0x100703bd: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x100703c2: mov      ebp, 0xf
0x100703c7: mov      eax, edi
0x100703c9: add      esp, 0xc
0x100703cc: mov      dword ptr [esp + 0xf8], ebp
0x100703d3: mov      dword ptr [esp + 0xf4], ebx
0x100703da: mov      byte ptr [esp + 0xe4], bl
0x100703e1: lea      edx, [eax + 1]
0x100703e4: mov      cl, byte ptr [eax]
0x100703e6: add      eax, 1
0x100703e9: cmp      cl, bl
0x100703eb: jne      0x100703e4 ; "À:Ëu÷+ÂPW$è"
0x100703ed: sub      eax, edx
0x100703ef: push     eax
0x100703f0: push     edi
0x100703f1: lea      ecx, [esp + 0xe8]
0x100703f8: call     0x100019e0 ; "SUVñNù^rëÃl$;èr1ùrëÃVÐ;ÕvùrD$P+ëUVÎèçýÿÿ^][Â"
0x100703fd: cmp      dword ptr [esp + 0xf4], ebx
0x10070404: mov      dword ptr [esp + 0x108], ebx
0x1007040b: jne      0x1007042e ; "ÙîL$8ÙT$8QÙT$@T$$ÙèRÙT$HD$4ÙÉPÙT$,L$PÙ\$0QÙÐë,Ù\$8ÙT$<ÙT$@Ù\$Dè=ÿ"
0x1007040d: cmp      dword ptr [esp + 0xf8], 0x10
0x10070415: jb       0x10070427
0x10070417: mov      eax, dword ptr [esp + 0xe4]
0x1007041e: push     eax
0x1007041f: call     0x100028e0 ; "W|$ÿtpS¶_ÿÛU¶oþVwþy<¸"
0x10070424: add      esp, 4
0x10070427: xor      eax, eax
0x10070429: jmp      0x1007094b ; "媽$"
0x1007042e: fldz     
0x10070430: lea      ecx, [esp + 0x38]
0x10070434: fst      dword ptr [esp + 0x38]
0x10070438: push     ecx
0x10070439: fst      dword ptr [esp + 0x40]
0x1007043d: lea      edx, [esp + 0x24]
0x10070441: fld1     
0x10070443: push     edx
0x10070444: fst      dword ptr [esp + 0x48]
0x10070448: lea      eax, [esp + 0x34]
0x1007044c: fxch     st(1)
0x1007044e: push     eax
0x1007044f: fst      dword ptr [esp + 0x2c]
0x10070453: lea      ecx, [esp + 0x50]
0x10070457: fstp     dword ptr [esp + 0x30]
0x1007045b: push     ecx
0x1007045c: fld      dword ptr [0x102cebd0]
0x10070462: fstp     dword ptr [esp + 0x38]
0x10070466: fst      dword ptr [esp + 0x3c]
0x1007046a: fst      dword ptr [esp + 0x40]
0x1007046e: fstp     dword ptr [esp + 0x44]
0x10070472: call     0x102603b4 ; "ÿ%ìä,ÿ%èä,ÿ%ää,ÿ%àä,ÿ%Üä,ÿ%Øä,ÿ%å,ÿ%å,ÿ%ôä,ÿ%xå,ÿ%tå,ÿ%på,ÿ%lå,ÿ%hå,ÿ%då,ÿ%`å,ÿ%\å,ÿ%Xå,ÿ%Tå,ÿ%På,ÿ%Lå,ÿ%Hå,ÿ%Då,ÿ%@å,ÿ%<å,ÿ%8å,ÿ%4å,ÿ%0å,ÿ%,å,ÿ%(å,ÿ%$å,ÿ% å,ÿ%å,ÿ%"
0x10070477: lea      edx, [esp + 0x44]
0x1007047b: push     edx
0x1007047c: push     2
0x1007047e: mov      ecx, 0x10f89ac0
0x10070483: call     0x10131530 ; "T$ÁÊéthétTéý"
0x10070488: fld      dword ptr [0x102d4148]
0x1007048e: mov      eax, dword ptr [0x10f8a6d8]
0x10070493: cdq      
0x10070494: idiv     dword ptr [0x10f8a6dc]
0x1007049a: sub      esp, 0x10
0x1007049d: fstp     dword ptr [esp + 0xc]
0x100704a1: fld      dword ptr [0x102d5534]
0x100704a7: fstp     dword ptr [esp + 8]
0x100704ab: mov      dword ptr [esp + 0x24], eax
0x100704af: fild     dword ptr [esp + 0x24]
0x100704b3: lea      eax, [esp + 0x94]
0x100704ba: fstp     dword ptr [esp + 4]
0x100704be: fld      dword ptr [0x102d685c]
0x100704c4: fstp     dword ptr [esp]
0x100704c7: push     eax
0x100704c8: call     0x102603ae ; "ÿ%ðä,ÿ%ìä,ÿ%èä,ÿ%ää,ÿ%àä,ÿ%Üä,ÿ%Øä,ÿ%å,ÿ%å,ÿ%ôä,ÿ%xå,ÿ%tå,ÿ%på,ÿ%lå,ÿ%hå,ÿ%då,ÿ%`å,ÿ%\å,ÿ%Xå,ÿ%Tå,ÿ%På,ÿ%Lå,ÿ%Hå,ÿ%Då,ÿ%@å,ÿ%<å,ÿ%8å,ÿ%4å,ÿ%0å,ÿ%,å,ÿ%(å,ÿ%$å,ÿ% å,ÿ%"
0x100704cd: lea      ecx, [esp + 0x44]
0x100704d1: push     ecx
0x100704d2: push     3
0x100704d4: mov      ecx, 0x10f89ac0
0x100704d9: call     0x10131530 ; "T$ÁÊéthétTéý"
0x100704de: mov      edi, dword ptr [esi + 0x1aac]
0x100704e4: cmp      edi, ebx
0x100704e6: je       0x100704fe
0x100704e8: mov      ecx, edi
0x100704ea: call     0x1013e120 ; "jÿhf,d¡"
0x100704ef: push     edi
0x100704f0: call     0x100028e0 ; "W|$ÿtpS¶_ÿÛU¶oþVwþy<¸"
0x100704f5: add      esp, 4
0x100704f8: mov      dword ptr [esi + 0x1aac], ebx
0x100704fe: push     1
0x10070500: push     0x221c
0x10070505: call     0x10002810 ; "V媡$兤V鑇{&"
0x1007050a: add      esp, 8
0x1007050d: mov      dword ptr [esp + 0x14], eax
0x10070511: cmp      eax, ebx
0x10070513: mov      byte ptr [esp + 0x108], 1
0x1007051b: je       0x10070526 ; "3繱Sh8h-垳$"
0x1007051d: mov      ecx, eax
0x1007051f: call     0x1013db50 ; "jÿhø,d¡"
0x10070524: jmp      0x10070528 ; "SSh8h-垳$"
0x10070526: xor      eax, eax
0x10070528: push     ebx
0x10070529: push     ebx
0x1007052a: push     0x102d6838 ; "After new(TYPE2_UNKNOWN) Terrain"
0x1007052f: mov      byte ptr [esp + 0x114], bl
0x10070536: mov      dword ptr [esi + 0x1aac], eax
0x1007053c: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x10070541: add      esp, 0xc
0x10070544: cmp      dword ptr [0x1036fcec], ebx
0x1007054a: je       0x10070560 ; "¬"
0x1007054c: mov      edx, dword ptr [esi + 0x1aac]
0x10070552: fld      dword ptr [0x102d6834]
0x10070558: fstp     dword ptr [edx + 0xfd4]
0x1007055e: jmp      0x10070572 ; "¬"
0x10070560: mov      eax, dword ptr [esi + 0x1aac]
0x10070566: fld      dword ptr [0x102d6830]
0x1007056c: fstp     dword ptr [eax + 0xfd4]
0x10070572: mov      eax, dword ptr [esi + 0x1aac]
0x10070578: mov      dword ptr [eax + 0x2058], 0x1001de40
0x10070582: push     4
0x10070584: push     0x102d6828 ; "map/"
0x10070589: lea      ecx, [esp + 0xcc]
0x10070590: mov      dword ptr [esp + 0xe4], ebp
0x10070597: mov      dword ptr [esp + 0xe0], ebx
0x1007059e: mov      byte ptr [esp + 0xd0], bl
0x100705a5: call     0x100019e0 ; "SUVñNù^rëÃl$;èr1ùrëÃVÐ;ÕvùrD$P+ëUVÎèçýÿÿ^][Â"
0x100705aa: push     -1
0x100705ac: push     ebx
0x100705ad: lea      ecx, [esp + 0xe8]
0x100705b4: push     ecx
0x100705b5: lea      ecx, [esp + 0xd0]
0x100705bc: mov      byte ptr [esp + 0x114], 2
0x100705c4: call     0x10001e40 ; "SUl$VW|$9}ñsèÝ%"
0x100705c9: push     1
0x100705cb: push     0x102cf284 ; "/"
0x100705d0: lea      ecx, [esp + 0xcc]
0x100705d7: call     0x10001d50 ; "SVñVúW^rëËD$;Ár1úrëË~ù;øvúrL$Q+ÃPVÎè§"
0x100705dc: push     -1
0x100705de: push     ebx
0x100705df: lea      edx, [esp + 0xe8]
0x100705e6: push     edx
0x100705e7: lea      ecx, [esp + 0xd0]
0x100705ee: call     0x10001e40 ; "SUl$VW|$9}ñsèÝ%"
0x100705f3: push     4
0x100705f5: push     0x102d6820 ; ".map"
0x100705fa: lea      ecx, [esp + 0xcc]
0x10070601: call     0x10001d50 ; "SVñVúW^rëËD$;Ár1úrëË~ù;øvúrL$Q+ÃPVÎè§"
0x10070606: mov      edi, dword ptr [esp + 0x114]
0x1007060d: cmp      edi, ebx
0x1007060f: jne      0x10070682 ; "SShüg-èb­"
0x10070611: mov      eax, dword ptr [esp + 0xc8]
0x10070618: mov      ebp, 0x10
0x1007061d: cmp      dword ptr [esp + 0xdc], ebp
0x10070624: jae      0x1007062d ; "ìü6Q¬"
0x10070626: lea      eax, [esp + 0xc8]
0x1007062d: mov      ecx, dword ptr [0x1036fcec]
0x10070633: push     ecx
0x10070634: mov      ecx, dword ptr [esi + 0x1aac]
0x1007063a: push     eax
0x1007063b: call     0x1015d6d0 ; "ìS\$VÃWñPÀÉu÷+ÂPS¸!"
0x10070640: test     eax, eax
0x10070642: jne      0x10070682 ; "SShüg-èb­"
0x10070644: cmp      dword ptr [esp + 0xdc], ebp
0x1007064b: jb       0x1007065d ; "9¬$ø"
0x1007064d: mov      edx, dword ptr [esp + 0xc8]
0x10070654: push     edx
0x10070655: call     0x100028e0 ; "W|$ÿtpS¶_ÿÛU¶oþVwþy<¸"
0x1007065a: add      esp, 4
0x1007065d: cmp      dword ptr [esp + 0xf8], ebp
0x10070664: mov      dword ptr [esp + 0xdc], 0xf
0x1007066f: mov      dword ptr [esp + 0xd8], ebx
0x10070676: mov      byte ptr [esp + 0xc8], bl
0x1007067d: jmp      0x10070415 ; "r$ä"
0x10070682: push     ebx
0x10070683: push     ebx
0x10070684: push     0x102d67fc ; "After Load Terrain Data From File"
0x10070689: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1007068e: mov      ecx, dword ptr [esp + 0x124]
0x10070695: mov      edx, dword ptr [esp + 0x128]
0x1007069c: add      esp, 0xc
0x1007069f: cmp      edi, ebx
0x100706a1: mov      dword ptr [esp + 0x14], ecx
0x100706a5: mov      dword ptr [esp + 0x18], edx
0x100706a9: jne      0x100706c5 ; "D$âÂøD$âÂèjhÄA"
0x100706ab: mov      eax, dword ptr [esi + 0x1aac]
0x100706b1: mov      ecx, dword ptr [eax + 0x1010]
0x100706b7: mov      edx, dword ptr [eax + 0x1014]
0x100706bd: mov      dword ptr [esp + 0x14], ecx
0x100706c1: mov      dword ptr [esp + 0x18], edx
0x100706c5: mov      eax, dword ptr [esp + 0x14]
0x100706c9: cdq      
0x100706ca: and      edx, 3
0x100706cd: add      eax, edx
0x100706cf: mov      edi, eax
0x100706d1: mov      eax, dword ptr [esp + 0x18]
0x100706d5: cdq      
0x100706d6: and      edx, 3
0x100706d9: add      eax, edx
0x100706db: mov      ebp, eax
0x100706dd: push     1
0x100706df: push     0x1041c4
0x100706e4: sar      edi, 2
0x100706e7: sar      ebp, 2
0x100706ea: call     0x10002810 ; "V媡$兤V鑇{&"
0x100706ef: add      esp, 8
0x100706f2: mov      dword ptr [esp + 0x1c], eax
0x100706f6: cmp      eax, ebx
0x100706f8: mov      byte ptr [esp + 0x108], 3
0x10070700: je       0x10070713 ; "3繱Sh詆-苿$"
0x10070702: push     esi
0x10070703: push     0x270f
0x10070708: push     ebp
0x10070709: push     edi
0x1007070a: mov      ecx, eax
0x1007070c: call     0x1006fe80 ; "jÿh!+d¡"
0x10070711: jmp      0x10070715 ; "SSh詆-苿$"
0x10070713: xor      eax, eax
0x10070715: push     ebx
0x10070716: push     ebx
0x10070717: push     0x102d67d4 ; "After new(TYPE2_UNKNOWN) SceneObj Array"
0x1007071c: mov      byte ptr [esp + 0x114], 2
0x10070724: mov      dword ptr [esi + 0xc], eax
0x10070727: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1007072c: push     1
0x1007072e: push     0x1041c4
0x10070733: mov      dword ptr [0x1037781c], 1
0x1007073d: call     0x10002810 ; "V媡$兤V鑇{&"
0x10070742: add      esp, 0x14
0x10070745: mov      dword ptr [esp + 0x1c], eax
0x10070749: cmp      eax, ebx
0x1007074b: mov      byte ptr [esp + 0x108], 4
0x10070753: je       0x10070766 ; "3繱Sh╣-苿$"
0x10070755: push     esi
0x10070756: push     0x514
0x1007075b: push     ebp
0x1007075c: push     edi
0x1007075d: mov      ecx, eax
0x1007075f: call     0x1006fad0 ; "jÿh +d¡"
0x10070764: jmp      0x10070768 ; "SSh╣-苿$"
0x10070766: xor      eax, eax
0x10070768: push     ebx
0x10070769: push     ebx
0x1007076a: push     0x102d67a8 ; "After new(TYPE2_UNKNOWN) StaticCha Array"
0x1007076f: mov      byte ptr [esp + 0x114], 2
0x10070777: mov      dword ptr [esi + 0x10], eax
0x1007077a: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x1007077f: push     1
0x10070781: push     0x1041c4
0x10070786: mov      dword ptr [0x1037781c], ebx
0x1007078c: call     0x10002810 ; "V媡$兤V鑇{&"
0x10070791: add      esp, 0x14
0x10070794: mov      dword ptr [esp + 0x1c], eax
0x10070798: cmp      eax, ebx
0x1007079a: mov      byte ptr [esp + 0x108], 5
0x100707a2: je       0x100707b5 ; "3繱Sh刧-苿$"
0x100707a4: push     esi
0x100707a5: push     0x1f4
0x100707aa: push     ebp
0x100707ab: push     edi
0x100707ac: mov      ecx, eax
0x100707ae: call     0x1006fad0 ; "jÿh +d¡"
0x100707b3: jmp      0x100707b7 ; "SSh刧-苿$"
0x100707b5: xor      eax, eax
0x100707b7: push     ebx
0x100707b8: push     ebx
0x100707b9: push     0x102d6784 ; "After new(TYPE2_UNKNOWN) Cha Array"
0x100707be: mov      byte ptr [esp + 0x114], 2
0x100707c6: mov      dword ptr [esi + 0x14], eax
0x100707c9: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x100707ce: push     0x754
0x100707d3: push     0xd4
0x100707d8: push     0x102d675c ; "sizeof(SceneObj) = %d, sizeof(Cha)=%d
"
0x100707dd: push     0x102d6588 ; "mem"
0x100707e2: call     0x10115fb0
0x100707e7: add      esp, 0x1c
0x100707ea: cmp      dword ptr [esp + 0x114], ebx
0x100707f1: mov      dword ptr [esi + 0x1ebc], ebx
0x100707f7: jne      0x1007082c ; "l$|$SSh<g-è°«"
0x100707f9: mov      eax, dword ptr [esi + 0x1aac]
0x100707ff: push     eax
0x10070800: lea      ecx, [esi + 0x1ec8]
0x10070806: call     0x100ecd70 ; "UìäÀì4SVñFÀWt	PèU[ñÿÄFÀt	PèE[ñÿÄ}"
0x1007080b: mov      ebp, dword ptr [esp + 0x18]
0x1007080f: mov      edi, dword ptr [esp + 0x14]
0x10070813: push     ebp
0x10070814: push     edi
0x10070815: lea      ecx, [esi + 0x1ef8]
0x1007081b: call     0x100f5140 ; "D$SUl$VWñjh"
0x10070820: mov      dword ptr [esi + 0x1f00], 1
0x1007082a: jmp      0x10070834 ; "SSh<g-è°«"
0x1007082c: mov      ebp, dword ptr [esp + 0x18]
0x10070830: mov      edi, dword ptr [esp + 0x14]
0x10070834: push     ebx
0x10070835: push     ebx
0x10070836: push     0x102d673c ; "before Create Pathfinding Data"
0x1007083b: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x10070840: add      esp, 0xc
0x10070843: cmp      dword ptr [0x10360c80], ebx
0x10070849: je       0x10070878 ; "¹8ý6èî£"
0x1007084b: mov      ecx, 0x1035f318
0x10070850: call     0x100ef7d0 ; "VñFPè1ñÿNQèû0ñÿRèó0ñÿÄ3À^ÃÌÌÌÌÌÌÌÌÌÌÌÌfD$T$VñfL$jh"
0x10070855: mov      ecx, dword ptr [esi + 0x1ed0]
0x1007085b: push     ecx
0x1007085c: lea      edx, [ebp*4]
0x10070863: push     edx
0x10070864: lea      eax, [edi*4]
0x1007086b: push     eax
0x1007086c: mov      ecx, 0x1035f318
0x10070871: call     0x100ef800 ; "f婦$婽$V嬹f婰$jh"
0x10070876: jmp      0x100708a3 ; "SShg-èA«"
0x10070878: mov      ecx, 0x1036fd38 ; " 4ó455U5_5d5i555È5Í5Ú5á5;6@66¢6¯6õ6ÿ67	7)737h7m7z77Û7à738B8N88888¸8Â8÷8ü8	99n9s9Ã9Ò9Þ9::#:(:H:R:::: :þ:;S;b;n;¤;®;³;¸;Ø;â;<<)<0<<<ã<ò<"
0x1007087d: call     0x100eac70 ; "V嬹儈"
0x10070882: mov      ecx, dword ptr [esi + 0x1ed0]
0x10070888: push     ecx
0x10070889: lea      edx, [ebp*4]
0x10070890: push     edx
0x10070891: lea      eax, [edi*4]
0x10070898: push     eax
0x10070899: mov      ecx, 0x1036fd38 ; " 4ó455U5_5d5i555È5Í5Ú5á5;6@66¢6¯6õ6ÿ67	7)737h7m7z77Û7à738B8N88888¸8Â8÷8ü8	99n9s9Ã9Ò9Þ9::#:(:H:R:::: :þ:;S;b;n;¤;®;³;¸;Ø;â;<<)<0<<<ã<ò<"
0x1007089e: call     0x100ead00 ; "婦$S媆$U媗$VW孄嬹塅(3蓩呛"
0x100708a3: push     ebx
0x100708a4: push     ebx
0x100708a5: push     0x102d671c ; "After Create Pathfinding Data"
0x100708aa: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x100708af: add      esp, 0xc
0x100708b2: push     0xa
0x100708b4: push     0x1e
0x100708b6: lea      ecx, [esi + 0x1f50]
0x100708bc: call     0x10070050 ; "jÿhx!+d¡"
0x100708c1: push     0xa
0x100708c3: push     1
0x100708c5: lea      ecx, [esi + 0x1f78]
0x100708cb: call     0x10070050 ; "jÿhx!+d¡"
0x100708d0: mov      ecx, dword ptr [0x1036fca8]
0x100708d6: mov      ecx, dword ptr [ecx + 0x7b4]
0x100708dc: mov      dword ptr [esi + 0x1a24], ecx
0x100708e2: call     0x100df800 ; "Ùì.Q¹Ì7Ù$è,ûÿÿÙèìÙT$ÙT$°Ù$¢Ì7h\Ì7Ç Ì7"
0x100708e7: push     ebx
0x100708e8: push     ebx
0x100708e9: push     0x102d6708 ; "Scene LoadMap End"
0x100708ee: call     0x1012b3f0 ; "冹(VWj(岲$3銮D$"
0x100708f3: mov      esi, 0x10
0x100708f8: add      esp, 0xc
0x100708fb: cmp      dword ptr [esp + 0xdc], esi
0x10070902: jb       0x10070914 ; "9´$ø"
0x10070904: mov      edx, dword ptr [esp + 0xc8]
0x1007090b: push     edx
0x1007090c: call     0x100028e0 ; "W|$ÿtpS¶_ÿÛU¶oþVwþy<¸"
0x10070911: add      esp, 4
0x10070914: cmp      dword ptr [esp + 0xf8], esi
0x1007091b: mov      dword ptr [esp + 0xdc], 0xf
0x10070926: mov      dword ptr [esp + 0xd8], ebx
0x1007092d: mov      byte ptr [esp + 0xc8], bl
0x10070934: jb       0x10070946
0x10070936: mov      eax, dword ptr [esp + 0xe4]
0x1007093d: push     eax
0x1007093e: call     0x100028e0 ; "W|$ÿtpS¶_ÿÛU¶oþVwþy<¸"
0x10070943: add      esp, 4
0x10070946: mov      eax, 1
0x1007094b: mov      ecx, dword ptr [esp + 0x100]
0x10070952: mov      dword ptr fs:[0], ecx
0x10070959: pop      ecx
0x1007095a: pop      edi
0x1007095b: pop      esi
0x1007095c: pop      ebp
0x1007095d: pop      ebx
0x1007095e: mov      ecx, dword ptr [esp + 0xe8]
0x10070965: xor      ecx, esp
0x10070967: call     0x10261f90 ; ";剈6u竺閸<"
0x1007096c: add      esp, 0xf8
0x10070972: ret      0x10
0x10070975: int3     
0x10070976: int3     
0x10070977: int3     
0x10070978: int3     
0x10070979: int3     
0x1007097a: int3     
0x1007097b: int3     
0x1007097c: int3     
0x1007097d: int3     
0x1007097e: int3     
0x1007097f: int3     
0x10070980: push     -1
0x10070982: push     0x102b22cf ; "T$BôJð3Èè°üúÿ¸g3éhùúÿÌÌÌÌÌÌ¡{7àþ£{7ÃT$BÀJ¼3ÈèüúÿÀJü3Èètüúÿ¸Èg3é,ùúÿÌÌÌÌÌÌÌÌÌÌM°éhôÔÿT$B¸J´3ÈèGüúÿ¸ôg3éÿøúÿÌÌÌÌÌÌÌÌÌÌÌÌÌEPMQèCíÔÿÄÃT$BJè3Èèüúÿ¸Th3éÆøúÿÌÌÌÌ¡¼{7à"
0x10070987: mov      eax, dword ptr fs:[0]
0x1007098d: push     eax
0x1007098e: push     ebx
0x1007098f: push     esi
0x10070990: push     edi
0x10070991: mov      eax, dword ptr [0x10367584]
0x10070996: xor      eax, esp
0x10070998: push     eax
0x10070999: lea      eax, [esp + 0x10]
0x1007099d: mov      dword ptr fs:[0], eax
0x100709a3: mov      edi, ecx
0x100709a5: cmp      dword ptr [edi + 0x1e90], 0x10
0x100709ac: jb       0x100709b6 ; "崌|"
0x100709ae: mov      eax, dword ptr [edi + 0x1e7c]
0x100709b4: jmp      0x100709bc ; "L$(T$$QL$$RQPÏèùÿÿÀu2ÀL$d"
0x100709b6: lea      eax, [edi + 0x1e7c]
0x100709bc: mov      ecx, dword ptr [esp + 0x28]
0x100709c0: mov      edx, dword ptr [esp + 0x24]
0x100709c4: push     ecx
0x100709c5: mov      ecx, dword ptr [esp + 0x24]
0x100709c9: push     edx
0x100709ca: push     ecx
0x100709cb: push     eax
0x100709cc: mov      ecx, edi
0x100709ce: call     0x10070370 ; "jÿh"+d¡"
0x100709d3: test     eax, eax
0x100709d5: jne      0x100709ee
0x100709d7: xor      al, al
0x100709d9: mov      ecx, dword ptr [esp + 0x10]
0x100709dd: mov      dword ptr fs:[0], ecx
0x100709e4: pop      ecx
0x100709e5: pop      edi
0x100709e6: pop      esi
0x100709e7: pop      ebx
0x100709e8: add      esp, 0xc
0x100709eb: ret      0xc
0x100709ee: push     1
0x100709f0: push     0x1600
0x100709f5: call     0x10002810 ; "V媡$兤V鑇{&"
0x100709fa: add      esp, 8
0x100709fd: mov      dword ptr [esp + 0x28], eax
0x10070a01: xor      ebx, ebx
0x10070a03: cmp      eax, ebx
0x10070a05: mov      dword ptr [esp + 0x18], ebx
0x10070a09: je       0x10070a2d ; "3鰤反"
0x10070a0b: push     0x10056470 ; "jÿh+d¡"
0x10070a10: push     0x10055fe0 ; "jÿhÿ+d¡"
0x10070a15: push     3
0x10070a17: lea      esi, [eax + 4]
0x10070a1a: push     0x754
0x10070a1f: push     esi
0x10070a20: mov      dword ptr [eax], 3
0x10070a26: call     0x10262e4c ; "jh姥4鑐&"
0x10070a2b: jmp      0x10070a2f ; "·´"
0x10070a2d: xor      esi, esi
0x10070a2f: mov      dword ptr [edi + 0x1eb4], esi
0x10070a35: mov      dword ptr [esp + 0x18], 0xffffffff
0x10070a3d: xor      esi, esi
0x10070a3f: nop      
0x10070a40: mov      edx, dword ptr [edi + 0x1eb4]
0x10070a46: mov      dword ptr [esi + edx + 4], ebx
0x10070a4a: mov      eax, dword ptr [edi + 0x1eb4]
0x10070a50: mov      edx, dword ptr [esi + eax]
0x10070a53: lea      ecx, [esi + eax]
0x10070a56: mov      eax, dword ptr [edx + 0xc]
0x10070a59: push     edi
0x10070a5a: call     eax
0x10070a5c: add      esi, 0x754
0x10070a62: add      ebx, 1
0x10070a65: cmp      esi, 0x15fc
0x10070a6b: jl       0x10070a40 ; "´"
0x10070a6d: push     0x400
0x10070a72: mov      ecx, edi
0x10070a74: call     0x1006dce0 ; "jÿh+d¡"
0x10070a79: push     0x102d6874 ; "Scene : LoadMap, CreateUICha, CreateShadeArray! OK!
"
0x10070a7e: push     0x102cea84 ; "init"
0x10070a83: call     0x10115fb0
0x10070a88: add      esp, 8
0x10070a8b: mov      al, 1

### InternalLoadMap? 0x1001bb20
0x1001bb20: push     ebx
0x1001bb21: mov      ebx, dword ptr [esp + 8]
0x1001bb25: push     esi
0x1001bb26: push     edi
0x1001bb27: mov      edi, ecx
0x1001bb29: lea      edx, [edi + 0x5b0]
0x1001bb2f: mov      eax, ebx
0x1001bb31: sub      edx, ebx
0x1001bb33: mov      cl, byte ptr [eax]
0x1001bb35: mov      byte ptr [edx + eax], cl
0x1001bb38: add      eax, 1
0x1001bb3b: test     cl, cl
0x1001bb3d: jne      0x1001bb33 ; "ÀÉuô3öVSÏè&ñÿÿÀtÆþ~ë_^¸"
0x1001bb3f: xor      esi, esi
0x1001bb41: push     esi
0x1001bb42: push     ebx
0x1001bb43: mov      ecx, edi
0x1001bb45: call     0x1001ac70 ; "jÿhèÂ*d¡"
0x1001bb4a: test     eax, eax
0x1001bb4c: je       0x1001bb61 ; "_^3À[Â"
0x1001bb4e: add      esi, 1
0x1001bb51: cmp      esi, 6
0x1001bb54: jle      0x1001bb41 ; "VSÏè&ñÿÿÀtÆþ~ë_^¸"
0x1001bb56: pop      edi
0x1001bb57: pop      esi
0x1001bb58: mov      eax, 1
0x1001bb5d: pop      ebx
0x1001bb5e: ret      4
0x1001bb61: pop      edi
0x1001bb62: pop      esi
0x1001bb63: xor      eax, eax
0x1001bb65: pop      ebx
0x1001bb66: ret      4
0x1001bb69: int3     
0x1001bb6a: int3     
0x1001bb6b: int3     
0x1001bb6c: int3     
0x1001bb6d: int3     
0x1001bb6e: int3     
0x1001bb6f: int3     
0x1001bb70: push     ecx
0x1001bb71: push     ebx
0x1001bb72: push     ebp
0x1001bb73: mov      ebp, dword ptr [esp + 0x14]
0x1001bb77: push     esi
0x1001bb78: mov      esi, ecx
0x1001bb7a: push     edi
0x1001bb7b: mov      edi, dword ptr [esi + 4]
0x1001bb7e: test     edi, edi
0x1001bb80: je       0x1001bb8e ; "3垭;鴙钀_$"
0x1001bb82: mov      eax, dword ptr [esi + 8]
0x1001bb85: mov      ecx, eax
0x1001bb87: sub      ecx, edi
0x1001bb89: sar      ecx, 2
0x1001bb8c: jne      0x1001bb92 ; ";鴙钀_$"
0x1001bb8e: xor      ebx, ebx
0x1001bb90: jmp      0x1001bbb1 ; "T$$D$ RjPUÎè«øÿÿ~;~vèY_$"
0x1001bb92: cmp      edi, eax
0x1001bb94: jbe      0x1001bb9b ; "呿t;顃鑳_$"
0x1001bb96: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bb9b: test     ebp, ebp
0x1001bb9d: je       0x1001bba3 ; "鑳_$"
0x1001bb9f: cmp      ebp, esi
0x1001bba1: je       0x1001bba8 ; "\$ +ßÁûT$$D$ RjPUÎè«øÿÿ~;~vèY_$"
0x1001bba3: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bba8: mov      ebx, dword ptr [esp + 0x20]
0x1001bbac: sub      ebx, edi
0x1001bbae: sar      ebx, 2
0x1001bbb1: mov      edx, dword ptr [esp + 0x24]
0x1001bbb5: mov      eax, dword ptr [esp + 0x20]
0x1001bbb9: push     edx
0x1001bbba: push     1
0x1001bbbc: push     eax
0x1001bbbd: push     ebp
0x1001bbbe: mov      ecx, esi
0x1001bbc0: call     0x1001b470 ; "D$SVñVÒL$u3ÀëF+ÂÁø\$Û"
0x1001bbc5: mov      edi, dword ptr [esi + 4]
0x1001bbc8: cmp      edi, dword ptr [esi + 8]
0x1001bbcb: jbe      0x1001bbd2 ; "|$ <;~w;~sèC_$"
0x1001bbcd: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bbd2: mov      dword ptr [esp + 0x20], edi
0x1001bbd6: lea      edi, [edi + ebx*4]
0x1001bbd9: cmp      edi, dword ptr [esi + 8]
0x1001bbdc: ja       0x1001bbe3 ; "鐲_$"
0x1001bbde: cmp      edi, dword ptr [esi + 4]
0x1001bbe1: jae      0x1001bbe8 ; "D$x_0^][YÂ"
0x1001bbe3: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bbe8: mov      eax, dword ptr [esp + 0x18]
0x1001bbec: mov      dword ptr [eax + 4], edi
0x1001bbef: pop      edi
0x1001bbf0: mov      dword ptr [eax], esi
0x1001bbf2: pop      esi
0x1001bbf3: pop      ebp
0x1001bbf4: pop      ebx
0x1001bbf5: pop      ecx
0x1001bbf6: ret      0x10
0x1001bbf9: int3     
0x1001bbfa: int3     
0x1001bbfb: int3     
0x1001bbfc: int3     
0x1001bbfd: int3     
0x1001bbfe: int3     
0x1001bbff: int3     
0x1001bc00: push     ecx
0x1001bc01: push     ebx
0x1001bc02: push     ebp
0x1001bc03: mov      ebp, dword ptr [esp + 0x14]
0x1001bc07: push     esi
0x1001bc08: mov      esi, ecx
0x1001bc0a: push     edi
0x1001bc0b: mov      edi, dword ptr [esi + 4]
0x1001bc0e: test     edi, edi
0x1001bc10: je       0x1001bc1e ; "3Ûë;øvè"
0x1001bc12: mov      eax, dword ptr [esi + 8]
0x1001bc15: mov      ecx, eax
0x1001bc17: sub      ecx, edi
0x1001bc19: sar      ecx, 2
0x1001bc1c: jne      0x1001bc22 ; ";øvè"
0x1001bc1e: xor      ebx, ebx
0x1001bc20: jmp      0x1001bc41 ; "T$$D$ RjPUÎèÛùÿÿ~;~vèÉ^$"
0x1001bc22: cmp      edi, eax
0x1001bc24: jbe      0x1001bc2b ; "呿t;顃梵^$"
0x1001bc26: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bc2b: test     ebp, ebp
0x1001bc2d: je       0x1001bc33 ; "梵^$"
0x1001bc2f: cmp      ebp, esi
0x1001bc31: je       0x1001bc38 ; "\$ +ßÁûT$$D$ RjPUÎèÛùÿÿ~;~vèÉ^$"
0x1001bc33: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bc38: mov      ebx, dword ptr [esp + 0x20]
0x1001bc3c: sub      ebx, edi
0x1001bc3e: sar      ebx, 2
0x1001bc41: mov      edx, dword ptr [esp + 0x24]
0x1001bc45: mov      eax, dword ptr [esp + 0x20]
0x1001bc49: push     edx
0x1001bc4a: push     1
0x1001bc4c: push     eax
0x1001bc4d: push     ebp
0x1001bc4e: mov      ecx, esi
0x1001bc50: call     0x1001b630 ; "D$SVñVÒL$u3ÀëF+ÂÁø\$Û"
0x1001bc55: mov      edi, dword ptr [esi + 4]
0x1001bc58: cmp      edi, dword ptr [esi + 8]
0x1001bc5b: jbe      0x1001bc62 ; "|$ <;~w;~sè³^$"
0x1001bc5d: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bc62: mov      dword ptr [esp + 0x20], edi
0x1001bc66: lea      edi, [edi + ebx*4]
0x1001bc69: cmp      edi, dword ptr [esi + 8]
0x1001bc6c: ja       0x1001bc73 ; "璩^$"
0x1001bc6e: cmp      edi, dword ptr [esi + 4]
0x1001bc71: jae      0x1001bc78 ; "D$x_0^][YÂ"
0x1001bc73: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bc78: mov      eax, dword ptr [esp + 0x18]
0x1001bc7c: mov      dword ptr [eax + 4], edi
0x1001bc7f: pop      edi
0x1001bc80: mov      dword ptr [eax], esi
0x1001bc82: pop      esi
0x1001bc83: pop      ebp
0x1001bc84: pop      ebx
0x1001bc85: pop      ecx
0x1001bc86: ret      0x10
0x1001bc89: int3     
0x1001bc8a: int3     
0x1001bc8b: int3     
0x1001bc8c: int3     
0x1001bc8d: int3     
0x1001bc8e: int3     
0x1001bc8f: int3     
0x1001bc90: push     ecx
0x1001bc91: push     ebx
0x1001bc92: push     ebp
0x1001bc93: mov      ebp, dword ptr [esp + 0x14]
0x1001bc97: push     esi
0x1001bc98: mov      esi, ecx
0x1001bc9a: push     edi
0x1001bc9b: mov      edi, dword ptr [esi + 4]
0x1001bc9e: test     edi, edi
0x1001bca0: je       0x1001bcae ; "3垭;鴙鑠^$"
0x1001bca2: mov      eax, dword ptr [esi + 8]
0x1001bca5: mov      ecx, eax
0x1001bca7: sub      ecx, edi
0x1001bca9: sar      ecx, 3
0x1001bcac: jne      0x1001bcb2 ; ";鴙鑠^$"
0x1001bcae: xor      ebx, ebx
0x1001bcb0: jmp      0x1001bcd1 ; "T$$D$ RjPUÎèûÿÿ~;~vè9^$"
0x1001bcb2: cmp      edi, eax
0x1001bcb4: jbe      0x1001bcbb ; "呿t;顃鑓^$"
0x1001bcb6: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bcbb: test     ebp, ebp
0x1001bcbd: je       0x1001bcc3 ; "鑓^$"
0x1001bcbf: cmp      ebp, esi
0x1001bcc1: je       0x1001bcc8 ; "\$ +ßÁûT$$D$ RjPUÎèûÿÿ~;~vè9^$"
0x1001bcc3: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bcc8: mov      ebx, dword ptr [esp + 0x20]
0x1001bccc: sub      ebx, edi
0x1001bcce: sar      ebx, 3
0x1001bcd1: mov      edx, dword ptr [esp + 0x24]
0x1001bcd5: mov      eax, dword ptr [esp + 0x20]
0x1001bcd9: push     edx
0x1001bcda: push     1
0x1001bcdc: push     eax
0x1001bcdd: push     ebp
0x1001bcde: mov      ecx, esi
0x1001bce0: call     0x1001b7f0 ; "Uìjÿh Ã*d¡"
0x1001bce5: mov      edi, dword ptr [esi + 4]
0x1001bce8: cmp      edi, dword ptr [esi + 8]
0x1001bceb: jbe      0x1001bcf2 ; "|$ <ß;~w;~sè#^$"
0x1001bced: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bcf2: mov      dword ptr [esp + 0x20], edi
0x1001bcf6: lea      edi, [edi + ebx*8]
0x1001bcf9: cmp      edi, dword ptr [esi + 8]
0x1001bcfc: ja       0x1001bd03 ; "è#^$"
0x1001bcfe: cmp      edi, dword ptr [esi + 4]
0x1001bd01: jae      0x1001bd08 ; "D$x_0^][YÂ"
0x1001bd03: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bd08: mov      eax, dword ptr [esp + 0x18]
0x1001bd0c: mov      dword ptr [eax + 4], edi
0x1001bd0f: pop      edi
0x1001bd10: mov      dword ptr [eax], esi
0x1001bd12: pop      esi
0x1001bd13: pop      ebp
0x1001bd14: pop      ebx
0x1001bd15: pop      ecx
0x1001bd16: ret      0x10
0x1001bd19: int3     
0x1001bd1a: int3     
0x1001bd1b: int3     
0x1001bd1c: int3     
0x1001bd1d: int3     
0x1001bd1e: int3     
0x1001bd1f: int3     
0x1001bd20: sub      esp, 8
0x1001bd23: push     ebx
0x1001bd24: push     esi
0x1001bd25: mov      esi, ecx
0x1001bd27: mov      ebx, dword ptr [esi + 8]
0x1001bd2a: cmp      dword ptr [esi + 4], ebx
0x1001bd2d: push     edi
0x1001bd2e: jbe      0x1001bd35 ; "媬;~v栝]$"
0x1001bd30: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bd35: mov      edi, dword ptr [esi + 4]
0x1001bd38: cmp      edi, dword ptr [esi + 8]
0x1001bd3b: jbe      0x1001bd42 ; "SVWVD$PÎèØÿÿ~;~vèÌ]$"
0x1001bd3d: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bd42: push     ebx
0x1001bd43: push     esi
0x1001bd44: push     edi
0x1001bd45: push     esi
0x1001bd46: lea      eax, [esp + 0x1c]
0x1001bd4a: push     eax
0x1001bd4b: mov      ecx, esi
0x1001bd4d: call     0x100195f0 ; "Ul$íVWùt;l$tè#$"
0x1001bd52: mov      edi, dword ptr [esi + 4]
0x1001bd55: cmp      edi, dword ptr [esi + 8]
0x1001bd58: jbe      0x1001bd5f ; "L$ T$$D$ QL$ RT$ PQRWVÎèãÿÿ_^[ÄÂ"
0x1001bd5a: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bd5f: mov      ecx, dword ptr [esp + 0x20]
0x1001bd63: mov      edx, dword ptr [esp + 0x24]
0x1001bd67: mov      eax, dword ptr [esp + 0x20]
0x1001bd6b: push     ecx
0x1001bd6c: mov      ecx, dword ptr [esp + 0x20]
0x1001bd70: push     edx
0x1001bd71: mov      edx, dword ptr [esp + 0x20]
0x1001bd75: push     eax
0x1001bd76: push     ecx
0x1001bd77: push     edx
0x1001bd78: push     edi
0x1001bd79: push     esi
0x1001bd7a: mov      ecx, esi
0x1001bd7c: call     0x1001a110 ; "D$ìÀUVñt;D$$tèz$"
0x1001bd81: pop      edi
0x1001bd82: pop      esi
0x1001bd83: pop      ebx
0x1001bd84: add      esp, 8
0x1001bd87: ret      0x14
0x1001bd8a: int3     
0x1001bd8b: int3     
0x1001bd8c: int3     
0x1001bd8d: int3     
0x1001bd8e: int3     
0x1001bd8f: int3     
0x1001bd90: sub      esp, 8
0x1001bd93: push     ebx
0x1001bd94: push     esi
0x1001bd95: mov      esi, ecx
0x1001bd97: mov      ebx, dword ptr [esi + 8]
0x1001bd9a: cmp      dword ptr [esi + 4], ebx
0x1001bd9d: push     edi
0x1001bd9e: jbe      0x1001bda5 ; "媬;~v鑩]$"
0x1001bda0: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bda5: mov      edi, dword ptr [esi + 4]
0x1001bda8: cmp      edi, dword ptr [esi + 8]
0x1001bdab: jbe      0x1001bdb2 ; "SVWVD$PÎèÎ×ÿÿ~;~vè\]$"
0x1001bdad: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bdb2: push     ebx
0x1001bdb3: push     esi
0x1001bdb4: push     edi
0x1001bdb5: push     esi
0x1001bdb6: lea      eax, [esp + 0x1c]
0x1001bdba: push     eax
0x1001bdbb: mov      ecx, esi
0x1001bdbd: call     0x10019590 ; "Ul$íVWùt;l$tè$"
0x1001bdc2: mov      edi, dword ptr [esi + 4]
0x1001bdc5: cmp      edi, dword ptr [esi + 8]
0x1001bdc8: jbe      0x1001bdcf ; "L$ T$$D$ QL$ RT$ PQRWVÎèoåÿÿ_^[ÄÂ"
0x1001bdca: call     0x10261b2b ; "3ÀPPPPPèÐÿÿÿÄÃUìì EVWjY¾41}àó¥EøEÀ_Eü^tö"
0x1001bdcf: mov      ecx, dword ptr [esp + 0x20]
0x1001bdd3: mov      edx, dword ptr [esp + 0x24]
0x1001bdd7: mov      eax, dword ptr [esp + 0x20]
0x1001bddb: push     ecx
0x1001bddc: mov      ecx, dword ptr [esp + 0x20]
0x1001bde0: push     edx
0x1001bde1: mov      edx, dword ptr [esp + 0x20]
0x1001bde5: push     eax
0x1001bde6: push     ecx
0x1001bde7: push     edx
0x1001bde8: push     edi
0x1001bde9: push     esi
0x1001bdea: mov      ecx, esi
0x1001bdec: call     0x1001a360 ; "婦$冹吚UV嬹t;D$$t璞w$"
0x1001bdf1: pop      edi
0x1001bdf2: pop      esi
0x1001bdf3: pop      ebx
0x1001bdf4: add      esp, 8
0x1001bdf7: ret      0x14
0x1001bdfa: int3     
0x1001bdfb: int3     
0x1001bdfc: int3     
0x1001bdfd: int3     
0x1001bdfe: int3     
0x1001bdff: int3     
0x1001be00: push     -1
0x1001be02: push     0x102ac348 ; "T$BàJÜ3Èè7\ûÿ¸è3éïXûÿÌÌÌÌÌÌÌÌÌÌÌÌÌMäéÈ3ÖÿT$BÜJØ3Èè\ûÿ¸3é¿XûÿÌÌÌÌÌÌÌÌÌÌÌÌÌMäé3ÖÿT$BÈJÄ3Èè×[ûÿ¸@3éXûÿÌÌÌÌÌÌÌÌÌÌÌÌÌMàé83ÖÿT$B¼J¸3Èè§[ûÿ¸l3é_XûÿÌÌÌÌÌÌÌÌÌÌÌÌÌMÐéx4ÖÿMàé03Öÿ"
0x1001be07: mov      eax, dword ptr fs:[0]
0x1001be0d: push     eax
0x1001be0e: sub      esp, 0x14
0x1001be11: push     ebx
0x1001be12: push     esi
0x1001be13: push     edi
0x1001be14: mov      eax, dword ptr [0x10367584]
0x1001be19: xor      eax, esp
0x1001be1b: push     eax
0x1001be1c: lea      eax, [esp + 0x24]
0x1001be20: mov      dword ptr fs:[0], eax
0x1001be26: mov      esi, ecx
0x1001be28: push     0x102d0518 ; "CGameApp::BeforeRunGameLogic"
0x1001be2d: lea      ecx, [esp + 0x14]
0x1001be31: call     0x1015ea70 ; "婦$V嬹j"
0x1001be36: mov      dword ptr [esp + 0x2c], 0
0x1001be3e: call     dword ptr [0x102ce2d0]
0x1001be44: mov      ecx, esi
0x1001be46: mov      edi, eax
0x1001be48: call     0x1012be90 ; "Vñè¨üÿÿ`"
0x1001be4d: mov      ebx, dword ptr [esi + 0x7b8]
0x1001be53: push     edi
0x1001be54: mov      ecx, ebx
0x1001be56: call     0x100e8a80 ; "ìTöê7SUl$`VWñuê7Åë¡ê7Õ+Ð3Û8ô"
0x1001be5b: mov      ecx, ebx
0x1001be5d: call     0x100e8990 ; "ÙÌ"
0x1001be62: lea      eax, [esp + 0x1c]
0x1001be66: push     eax
0x1001be67: call     dword ptr [0x102ce3c0]
0x1001be6d: mov      edx, dword ptr [esi + 8]
0x1001be70: lea      ecx, [esp + 0x14]
0x1001be74: push     ecx
0x1001be75: push     edx
0x1001be76: mov      dword ptr [esp + 0x1c], 0
0x1001be7e: mov      dword ptr [esp + 0x20], 0
0x1001be86: call     dword ptr [0x102ce3fc]
0x1001be8c: mov      ecx, dword ptr [esp + 0x1c]
0x1001be90: sub      ecx, dword ptr [esp + 0x14]
0x1001be94: mov      eax, dword ptr [esp + 0x20]
0x1001be98: sub      eax, dword ptr [esp + 0x18]
0x1001be9c: mov      dword ptr [esi + 0x554], ecx
0x1001bea2: push     edi
0x1001bea3: lea      ecx, [esi + 0x7fc]
0x1001bea9: mov      dword ptr [esi + 0x558], eax
0x1001beaf: call     0x100e7850 ; "VñN(ÉW|$tWÿÒN,ÉtWÿÒN$ÉtkWÿÒ~$ÿÆF0"
0x1001beb4: mov      ecx, dword ptr [0x1036fdb0]
0x1001beba: test     ecx, ecx
0x1001bebc: je       0x1001becb ; "Îè~ûÿÿL$ÇD$,ÿÿÿÿè½+"
0x1001bebe: mov      eax, dword ptr [ecx]
0x1001bec0: mov      edx, dword ptr [0x1036fdb4]
0x1001bec6: mov      eax, dword ptr [eax]
0x1001bec8: push     edx
0x1001bec9: call     eax
0x1001becb: mov      ecx, esi
0x1001becd: call     0x1001ba50 ; "QVñ"
0x1001bed2: lea      ecx, [esp + 0x10]
0x1001bed6: mov      dword ptr [esp + 0x2c], 0xffffffff
0x1001bede: call     0x1015eaa0 ; "Ç4ï.èeýÿÿÈé.õÿÿÌÌÌÌÌÌÌÌÌÌÌÌÌÌVñÇ4ï.èBýÿÿÈèõÿÿöD$t	Vèþ=êÿÄÆ^Â"
0x1001bee3: mov      ecx, dword ptr [esp + 0x24]
0x1001bee7: mov      dword ptr fs:[0], ecx
0x1001beee: pop      ecx
0x1001beef: pop      edi
0x1001bef0: pop      esi
0x1001bef1: pop      ebx
0x1001bef2: add      esp, 0x20
0x1001bef5: ret      
0x1001bef6: int3     
0x1001bef7: int3     
0x1001bef8: int3     
0x1001bef9: int3     
0x1001befa: int3     
0x1001befb: int3     
0x1001befc: int3     
0x1001befd: int3     
0x1001befe: int3     
0x1001beff: int3     
0x1001bf00: sub      esp, 0x2c
0x1001bf03: cmp      byte ptr [0x103711a0], 0
0x1001bf0a: push     ebx
0x1001bf0b: push     ebp
0x1001bf0c: push     esi
0x1001bf0d: push     edi
0x1001bf0e: mov      esi, ecx
0x1001bf10: jne      0x1001bf64 ; "=Ðâ,ÿ×¹¨D8èè(É"
0x1001bf12: call     0x10153f60 ; "¸¨eúÃÌÌÌÌÌÌÌÌÌÌVñÀW|$t;tè¤Û"
0x1001bf17: mov      ebp, eax
0x1001bf19: mov      edi, dword ptr [ebp]
0x1001bf1c: push     0x10056980 ; "jÿhè+d¡"
0x1001bf21: add      edi, 0xc
0x1001bf24: call     0x10055300 ; "¸ P-ÃÌÌÌÌÌÌÌÌÌÌD$L$Ç"
0x1001bf29: push     eax
0x1001bf2a: mov      eax, dword ptr [edi]
0x1001bf2c: mov      ecx, ebp
0x1001bf2e: call     eax
0x1001bf30: call     0x10153f60 ; "¸¨eúÃÌÌÌÌÌÌÌÌÌÌVñÀW|$t;tè¤Û"
0x1001bf35: mov      ebp, eax
0x1001bf37: mov      edi, dword ptr [ebp]
0x1001bf3a: push     0x1000d6b0 ; "¡¨ü6ÀL$T$t "
0x1001bf3f: add      edi, 0xc
0x1001bf42: call     0x1000d6a0 ; "¸°ì,ÃÌÌÌÌÌÌÌÌÌÌ¡¨ü6ÀL$T$t "
0x1001bf47: mov      edx, dword ptr [edi]
0x1001bf49: push     eax
0x1001bf4a: mov      ecx, ebp
0x1001bf4c: call     edx
0x1001bf4e: call     0x10055330 ; "è+ì"
0x1001bf53: call     0x1007b110 ; "èK"
0x1001bf58: call     0x10055d80 ; "jÿh+d¡"
0x1001bf5d: mov      byte ptr [0x103711a0], 1
0x1001bf64: mov      edi, dword ptr [0x102ce2d0]
0x1001bf6a: call     edi
0x1001bf6c: mov      ecx, 0x103844a8 ; "Ã2Î2H3b333§324N4 525r5}55u6¤6>788«8Ê89´9a:Ý:3;R;;<ú<>$>>>¢>«>²>Ñ>I???½?Å?Ñ?Ù?í?ø?ý?"
0x1001bf71: mov      ebp, eax
0x1001bf73: call     0x100f88a0 ; "jÿhËß+d¡"
0x1001bf78: mov      ecx, dword ptr [0x10370168]
0x1001bf7e: test     ecx, ecx
0x1001bf80: jne      0x1001bf8a ; "= ò5"
0x1001bf82: mov      ecx, ebp
0x1001bf84: mov      dword ptr [0x10370168], ecx
0x1001bf8a: cmp      dword ptr [0x1035f220], 0
0x1001bf91: mov      edx, dword ptr [esi + 0x7f4]
0x1001bf97: mov      dword ptr [esp + 0x10], edx
0x1001bf9b: jne      0x1001bfde ; "-h7Ç"
0x1001bf9d: test     edx, edx
0x1001bf9f: je       0x1001bfde ; "-h7Ç"
0x1001bfa1: mov      ebx, dword ptr [esi + 0x688]
0x1001bfa7: imul     ebx, edx
0x1001bfaa: mov      eax, ebp
0x1001bfac: sub      eax, ebx
0x1001bfae: sub      eax, ecx
0x1001bfb0: js       0x1001c2c1 ; "_^][Ä,ÃÌÌÌÌÌÌÌìVñVÒu3ÉëN+ÊÁùÒt$F+ÂÁø;ÈsFL$ÀF^ÄÂ"
0x1001bfb6: lea      ecx, [edx + edx]
0x1001bfb9: cmp      eax, ecx
0x1001bfbb: jbe      0x1001bfee ; "¡hXPè("
0x1001bfbd: call     0x1010ad30 ; "3纅9礠X斃锰烫】QX锰烫烫烫烫獭肣X锰烫烫烫烫蘤婦$f="
0x1001bfc2: test     eax, eax
0x1001bfc4: je       0x1001bfee ; "¡hXPè("
0x1001bfc6: call     edi
0x1001bfc8: mov      edx, dword ptr [esi + 0x688]
0x1001bfce: imul     edx, dword ptr [esi + 0x7f4]
0x1001bfd5: sub      eax, edx
0x1001bfd7: mov      dword ptr [0x10370168], eax
0x1001bfdc: jmp      0x1001bfee ; "¡hXPè("
0x1001bfde: mov      dword ptr [0x10370168], ebp
0x1001bfe4: mov      dword ptr [esi + 0x688], 0
0x1001bfee: mov      eax, dword ptr [0x10589968]
0x1001bff3: push     eax
0x1001bff4: call     0x1015e810 ; "jÿhî,d¡"
0x1001bff9: mov      ecx, eax
0x1001bffb: call     0x1015e740 ; "V嬹儈0"
0x1001c000: push     0
0x1001c002: push     0x102d0598 ; "CGameApp::Run"
0x1001c007: call     0x1015e810 ; "jÿhî,d¡"
0x1001c00c: mov      ecx, eax
0x1001c00e: call     0x1015e880
0x1001c013: mov      ebx, dword ptr [0x102ce2bc]
0x1001c019: lea      ecx, [esp + 0x24]
0x1001c01d: push     ecx
0x1001c01e: call     ebx
0x1001c020: push     0
0x1001c022: mov      edi, 1
0x1001c027: add      dword ptr [esi + 0x688], edi
0x1001c02d: push     0x3e8
0x1001c032: lea      ecx, [esp + 0x34]
0x1001c036: call     0x10017020 ; "ì=@6Vñu=D$PÿÀâ,ßl$ßl$Ù|$·D$Þù"
0x1001c03b: lea      edx, [esp + 0x2c]
0x1001c03f: push     edx
0x1001c040: call     ebx
0x1001c042: mov      eax, dword ptr [esi + 0x688]
0x1001c048: cmp      eax, 0xa
0x1001c04b: jg       0x1001c073 ; "Îèýÿÿ¾D"
0x1001c04d: mov      ecx, dword ptr [0x10f8b810]
0x1001c053: mov      edx, dword ptr [0x10589968]
0x1001c059: push     0x102d0584 ; "BeforeRunGameLogic"
0x1001c05e: push     ecx
0x1001c05f: push     edx
0x1001c060: push     eax
0x1001c061: push     0x102cfba0 ; "runcnt=[%d] frame=[%d] render=[%d] enter:%s
"
0x1001c066: push     0x102cea84 ; "init"
0x1001c06b: call     0x10115fb0
0x1001c070: add      esp, 0x18
0x1001c073: mov      ecx, esi
0x1001c075: call     0x1001be00 ; "jÿhHÃ*d¡"
0x1001c07a: cmp      dword ptr [esi + 0xc44], 0
0x1001c081: jne      0x1001c124
0x1001c087: cmp      dword ptr [0x1037e3b0], 0
0x1001c08e: je       0x1001c0a9 ; "èì"
0x1001c090: mov      ecx, 0x1037e360 ; "Û<ì<ð<ö<	== =%=,=2=A=E=K=S=a=e=k=|====¬=°=µ=¼=Â=Ñ=Õ=Û=ã=ñ=õ=û=>>>)><>@>E>L>R>a>e>k>s>>>>> >¦>¹>Ì>Ð>Õ>Ü>â>ñ>õ>û>????,?0?6?I?\?`?e?l?r?????¡?¥?«?¼?À?Æ?Ù?ì?ð?õ?ü?"
0x1001c095: call     0x100e14c0 ; "Vñ¨ü6ÉtS=hX
rL~dvF>"
0x1001c09a: cmp      dword ptr [0x1037e3b4], 0
0x1001c0a1: jne      0x1001c2c1 ; "_^][Ä,ÃÌÌÌÌÌÌÌìVñVÒu3ÉëN+ÊÁùÒt$F+ÂÁø;ÈsFL$ÀF^ÄÂ"
0x1001c0a7: jmp      0x1001c124
0x1001c0a9: call     0x1010ad30 ; "3纅9礠X斃锰烫】QX锰烫烫烫烫獭肣X锰烫烫烫烫蘤婦$f="
0x1001c0ae: test     eax, eax
0x1001c0b0: je       0x1001c0bb ; "媶L"
0x1001c0b2: mov      ecx, esi
0x1001c0b4: call     0x100179d0 ; "jÿhkÀ*d¡"
0x1001c0b9: jmp      0x1001c124
0x1001c0bb: mov      eax, dword ptr [esi + 0x84c]
0x1001c0c1: cmp      eax, 0x10
0x1001c0c4: ja       0x1001c0ca ; "壘L"
0x1001c0c6: cmp      eax, edi
0x1001c0c8: jae      0x1001c0d0 ; "3ÿ9¾L"
0x1001c0ca: mov      dword ptr [esi + 0x84c], edi
0x1001c0d0: xor      edi, edi
0x1001c0d2: cmp      dword ptr [esi + 0x84c], edi
0x1001c0d8: jbe      0x1001c11f
0x1001c0da: lea      ebx, [ebx]
0x1001c0e0: mov      ecx, esi
0x1001c0e2: call     0x100179d0 ; "jÿhkÀ*d¡"
0x1001c0e7: mov      eax, dword ptr [esi + 0x84c]
0x1001c0ed: mov      ecx, dword ptr [esi + 0x7f4]
0x1001c0f3: push     edi
0x1001c0f4: push     eax
0x1001c0f5: push     ecx
0x1001c0f6: push     0x102d0574 ; "[%d] [%dX] [%d]"
0x1001c0fb: push     0x140
0x1001c100: push     0x1f4
0x1001c105: push     3
0x1001c107: push     0x10f89ac0
0x1001c10c: call     0x10135c90 ; "S媆$U媗$兗珮"
0x1001c111: add      edi, 1
0x1001c114: add      esp, 0x20
0x1001c117: cmp      edi, dword ptr [esi + 0x84c]
0x1001c11d: jb       0x1001c0e0 ; "Îèé¸ÿÿL"
0x1001c11f: mov      edi, 1
0x1001c124: mov      edx, dword ptr [0x10589968]
0x1001c12a: sub      edx, dword ptr [0x1037016c]
0x1001c130: mov      eax, dword ptr [esi + 0x84c]
0x1001c136: mov      ecx, dword ptr [esi + 0x7f4]
0x1001c13c: push     edi
0x1001c13d: push     edx
0x1001c13e: push     eax
0x1001c13f: push     ecx
0x1001c140: push     0x102d0554 ; "[%d] [%dX] [%d] 游戏模式:[%d]"
0x1001c145: push     0x136
0x1001c14a: push     0x1f4
0x1001c14f: push     3
0x1001c151: push     0x10f89ac0
0x1001c156: call     0x10135c90 ; "S媆$U媗$兗珮"
0x1001c15b: mov      ecx, dword ptr [0x10589968]
0x1001c161: mov      dword ptr [0x1037016c], ecx
0x1001c167: mov      eax, dword ptr [esi + 0x688]
0x1001c16d: add      esp, 0x24
0x1001c170: cmp      eax, 0xa
0x1001c173: jg       0x1001c195 ; "ÎètÍÿÿD$PÿÓD$+D$,3Ò÷5@6ö7D$4u	=7-7= ò5"
0x1001c175: mov      edx, dword ptr [0x10f8b810]
0x1001c17b: push     0x102d0540 ; "AfterRunGameLogic"
0x1001c180: push     edx
0x1001c181: push     ecx
0x1001c182: push     eax
0x1001c183: push     0x102cfba0 ; "runcnt=[%d] frame=[%d] render=[%d] enter:%s
"
0x1001c188: push     0x102cea84 ; "init"
0x1001c18d: call     0x10115fb0
0x1001c192: add      esp, 0x18
0x1001c195: mov      ecx, esi
0x1001c197: call     0x10018f10 ; "jÿh¨À*d¡"
0x1001c19c: lea      eax, [esp + 0x14]

### CreateMap_export 0x1010b730
0x1010b730: mov      ecx, dword ptr [0x1036fca8]
0x1010b736: test     ecx, ecx
0x1010b738: je       0x1010b7e4 ; "锰烫烫烫烫烫億$"
0x1010b73e: cmp      dword ptr [0x1036fdb0], 0
0x1010b745: push     ebx
0x1010b746: mov      ebx, dword ptr [esp + 0x10]
0x1010b74a: push     esi
0x1010b74b: mov      esi, dword ptr [esp + 0x10]
0x1010b74f: push     edi
0x1010b750: mov      edi, dword ptr [esp + 0x10]
0x1010b754: jne      0x1010b760 ; "°ý6èõZöÿ¨ü6èº"
0x1010b756: push     esi
0x1010b757: push     edi
0x1010b758: push     1
0x1010b75a: push     ebx
0x1010b75b: call     0x10019e50 ; "jÿhGÁ*d¡"
0x1010b760: mov      ecx, dword ptr [0x1036fdb0]
0x1010b766: call     0x10071260 ; "SVñW¾¬"
0x1010b76b: mov      ecx, dword ptr [0x1036fca8]
0x1010b771: call     0x1012ba30 ; "è"
0x1010b776: mov      ecx, dword ptr [0x1036fdb0]
0x1010b77c: push     esi
0x1010b77d: push     edi
0x1010b77e: push     1
0x1010b780: call     0x10070980 ; "jÿhÏ"+d¡"
0x1010b785: mov      eax, dword ptr [esp + 0x1c]
0x1010b789: mov      ecx, dword ptr [0x1036fdb0]
0x1010b78f: mov      ecx, dword ptr [ecx + 0x1aac]
0x1010b795: push     eax
0x1010b796: push     ebx
0x1010b797: push     esi
0x1010b798: push     edi
0x1010b799: call     0x1015d980 ; "ì¨"
0x1010b79e: mov      eax, dword ptr [0x1036fdb0]
0x1010b7a3: mov      edx, dword ptr [eax + 0x1aac]
0x1010b7a9: push     edx
0x1010b7aa: lea      ecx, [eax + 0x1ec8]
0x1010b7b0: call     0x100ecd70 ; "UìäÀì4SVñFÀWt	PèU[ñÿÄFÀt	PèE[ñÿÄ}"
0x1010b7b5: mov      ecx, dword ptr [0x1036fdb0]
0x1010b7bb: push     esi
0x1010b7bc: push     edi
0x1010b7bd: add      ecx, 0x1ef8
0x1010b7c3: call     0x100f5140 ; "D$SUl$VWñjh"
0x1010b7c8: mov      ecx, dword ptr [0x1036fdb0]
0x1010b7ce: call     0x10071820 ; "VWùOèDýÿÿG3ö9p~@°jèýþÿGÆ;p|èOèýÿÿO_^éýÿÿQSUl$VñW~ÿtFÈ+ÏÁùu3Ûë;øvè "
0x1010b7d3: mov      ecx, dword ptr [0x1036fdb0]
0x1010b7d9: pop      edi
0x1010b7da: pop      esi
0x1010b7db: add      ecx, 0x18
0x1010b7de: pop      ebx
0x1010b7df: jmp      0x1006bbf0
0x1010b7e4: ret      
0x1010b7e5: int3     
0x1010b7e6: int3     
0x1010b7e7: int3     
0x1010b7e8: int3     
0x1010b7e9: int3     
0x1010b7ea: int3     
0x1010b7eb: int3     
0x1010b7ec: int3     
0x1010b7ed: int3     
0x1010b7ee: int3     
0x1010b7ef: int3     
0x1010b7f0: cmp      dword ptr [esp + 8], 0
0x1010b7f5: mov      ecx, dword ptr [esp + 4]
0x1010b7f9: mov      edx, dword ptr [0x1036fdb0]
0x1010b7ff: setne    al
0x1010b802: push     eax
0x1010b803: push     ecx
0x1010b804: mov      ecx, dword ptr [edx + 0x1aac]
0x1010b80a: call     0x1015cd90 ; "jÿhK,d¡"
0x1010b80f: ret      
0x1010b810: mov      eax, dword ptr [esp + 4]
0x1010b814: mov      ecx, dword ptr [0x1036fdb0]
0x1010b81a: mov      ecx, dword ptr [ecx + 0x1aac]
0x1010b820: push     eax
0x1010b821: call     0x1015d030
0x1010b826: ret      
0x1010b827: int3     
0x1010b828: int3     
0x1010b829: int3     
0x1010b82a: int3     
0x1010b82b: int3     
0x1010b82c: int3     
0x1010b82d: int3     
0x1010b82e: int3     
0x1010b82f: int3     
0x1010b830: mov      eax, dword ptr [0x1036fca8]
0x1010b835: add      eax, 0x5b0
0x1010b83a: ret      
0x1010b83b: int3     
0x1010b83c: int3     
0x1010b83d: int3     
0x1010b83e: int3     
0x1010b83f: int3     
0x1010b840: mov      eax, dword ptr [0x1036fca8]
0x1010b845: add      eax, 0x5f0
0x1010b84a: ret      
0x1010b84b: int3     
0x1010b84c: int3     
0x1010b84d: int3     
0x1010b84e: int3     
0x1010b84f: int3     
0x1010b850: push     esi
0x1010b851: mov      esi, dword ptr [esp + 8]
0x1010b855: test     esi, esi
0x1010b857: je       0x1010b87d ; "^ÃÌ°ý6Ét&D$ÀtÙD$PD$ìÙ\$ÙD$Ù$PèRöÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ°ý6Ét6D$Àt.ÙD$PD$ìÙ\$ÙD$$Ù\$ÙD$ Ù\$ÙD$Ù$PèQköÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b859: mov      eax, dword ptr [0x1036fca8]
0x1010b85e: add      eax, 0x5b0
0x1010b863: push     eax
0x1010b864: push     eax
0x1010b865: push     0x102d4104 ; "map/%s/%s.map"
0x1010b86a: push     0x10585918

### xref map/%s/%s.map 0x10050300
0x10050300: add      byte ptr [eax], al
0x10050302: add      byte ptr [ebx - 0x222f0032], cl
0x10050308: pop      esp
0x10050309: and      al, 0x1c
0x1005030b: push     1
0x1005030d: push     -1
0x1005030f: mov      ecx, esi
0x10050311: call     0x1023d4a0 ; "è+éÿÿÈéDzÿÿÌÌÌÌQ¹"
0x10050316: fmul     qword ptr [esp + 0x14]
0x1005031a: call     0x10263430
0x1005031f: push     eax
0x10050320: mov      ecx, esi
0x10050322: call     0x1023d490 ; "è;éÿÿÈézÿÿÌÌÌÌè+éÿÿÈéDzÿÿÌÌÌÌQ¹"
0x10050327: fmul     qword ptr [esp + 0x10]
0x1005032b: call     0x10263430
0x10050330: push     eax
0x10050331: mov      ecx, esi
0x10050333: call     0x1023d4a0 ; "è+éÿÿÈéDzÿÿÌÌÌÌQ¹"
0x10050338: fmul     qword ptr [esp + 0x24]
0x1005033c: call     0x10263430
0x10050341: push     eax
0x10050342: mov      ecx, esi
0x10050344: call     0x1023d490 ; "è;éÿÿÈézÿÿÌÌÌÌè+éÿÿÈéDzÿÿÌÌÌÌQ¹"
0x10050349: fmul     qword ptr [esp + 0x30]
0x1005034d: call     0x10263430
0x10050352: mov      ecx, dword ptr [esi + 0xc58]
0x10050358: push     eax
0x10050359: push     ecx
0x1005035a: mov      ecx, 0x103766f8 ; "6=^=j===Ä=Ð=é=>*>6>O>h>>>µ>Î>ö>??4?\?h???Â?Î?ç?"
0x1005035f: call     0x10023600 ; "D$T$PD$PPPPD$$RT$$PD$$RT$$PRèåëÿÿÂ"
0x10050364: pop      esi
0x10050365: add      esp, 0x20
0x10050368: ret      
0x10050369: int3     
0x1005036a: int3     
0x1005036b: int3     
0x1005036c: int3     
0x1005036d: int3     
0x1005036e: int3     
0x1005036f: int3     
0x10050370: sub      esp, 0x118
0x10050376: mov      eax, dword ptr [0x10367584]
0x1005037b: xor      eax, esp
0x1005037d: mov      dword ptr [esp + 0x114], eax
0x10050384: mov      eax, dword ptr [0x1036fca8]
0x10050389: push     ebp
0x1005038a: push     esi
0x1005038b: add      eax, 0x5b0
0x10050390: push     eax
0x10050391: push     eax
0x10050392: lea      eax, [esp + 0x24]
0x10050396: push     0x102d4104 ; "map/%s/%s.map"
0x1005039b: push     eax
0x1005039c: mov      ebp, ecx
0x1005039e: call     0x10263225 ; "Uìì S3Û9]uèD"
0x100503a3: lea      ecx, [esp + 0x2c]
0x100503a7: push     0x102d020c ; "rb"
0x100503ac: push     ecx
0x100503ad: call     0x1026453b ; "j@ÿt$ÿt$è-ÿÿÿÄÃVW|$3ö;þuèb1"
0x100503b2: mov      esi, eax
0x100503b4: add      esp, 0x18
0x100503b7: test     esi, esi
0x100503b9: je       0x100504e3
0x100503bf: push     2
0x100503c1: push     -8
0x100503c3: push     esi
0x100503c4: call     0x10262bd6 ; "jh@Ñ4èÖ("
0x100503c9: push     esi
0x100503ca: push     1
0x100503cc: lea      edx, [esp + 0x2c]
0x100503d0: push     4
0x100503d2: push     edx
0x100503d3: call     0x1026445c ; "ÿt$ÿt$ÿt$jÿÿt$èSÿÿÿÄÃjh Ò4è5"
0x100503d8: add      esp, 0x1c
0x100503db: test     eax, eax
0x100503dd: je       0x100504da ; "Vè/(!"
0x100503e3: push     edi
0x100503e4: push     esi
0x100503e5: push     1
0x100503e7: lea      eax, [esp + 0x1c]
0x100503eb: push     4
0x100503ed: push     eax
0x100503ee: call     0x1026445c ; "ÿt$ÿt$ÿt$jÿÿt$èSÿÿÿÄÃjh Ò4è5"
0x100503f3: mov      ecx, dword ptr [esp + 0x2c]
0x100503f7: push     0
0x100503f9: push     ecx
0x100503fa: push     esi
0x100503fb: call     0x10262bd6 ; "jh@Ñ4èÖ("
0x10050400: xor      edi, edi
0x10050402: add      esp, 0x1c
0x10050405: cmp      dword ptr [esp + 0x14], edi
0x10050409: jle      0x100504d9 ; "_Vè/(!"
0x1005040f: nop      
0x10050410: push     esi
0x10050411: push     4
0x10050413: lea      edx, [esp + 0x14]
0x10050417: push     1
0x10050419: push     edx
0x1005041a: call     0x1026445c ; "ÿt$ÿt$ÿt$jÿÿt$èSÿÿÿÄÃjh Ò4è5"
0x1005041f: push     esi
0x10050420: push     1
0x10050422: lea      eax, [esp + 0x30]
0x10050426: push     4
0x10050428: push     eax
0x10050429: call     0x1026445c ; "ÿt$ÿt$ÿt$jÿÿt$èSÿÿÿÄÃjh Ò4è5"
0x1005042e: push     esi
0x1005042f: push     1
0x10050431: lea      ecx, [esp + 0x38]
0x10050435: push     4
0x10050437: push     ecx
0x10050438: call     0x1026445c ; "ÿt$ÿt$ÿt$jÿÿt$èSÿÿÿÄÃjh Ò4è5"
0x1005043d: mov      eax, dword ptr [esp + 0x3c]
0x10050441: add      esp, 0x30
0x10050444: cmp      al, 0x4d
0x10050446: jne      0x1005045a ; "兦;|$|t婽$j"
0x10050448: cmp      ah, al
0x1005044a: jne      0x1005045a ; "兦;|$|t婽$j"
0x1005044c: cmp      byte ptr [esp + 0xe], 0x41
0x10050451: jne      0x1005045a ; "兦;|$|t婽$j"
0x10050453: cmp      byte ptr [esp + 0xf], 0x50
0x10050458: je       0x10050465 ; "婽$j"
0x1005045a: add      edi, 1
0x1005045d: cmp      edi, dword ptr [esp + 0x14]
0x10050461: jl       0x10050410 ; "VjT$jRè=@!"
0x10050463: jmp      0x100504d9 ; "_Vè/(!"
0x10050465: mov      edx, dword ptr [esp + 0x18]
0x10050469: push     0
0x1005046b: push     edx
0x1005046c: push     esi
0x1005046d: call     0x10262bd6 ; "jh@Ñ4èÖ("
0x10050472: mov      eax, dword ptr [esp + 0x1c]
0x10050476: push     1
0x10050478: push     eax
0x10050479: call     0x10002810 ; "V媡$兤V鑇{&"
0x1005047e: mov      edi, eax

### xref map/%s/%s.map2 0x1010b840
0x1010b840: mov      eax, dword ptr [0x1036fca8]
0x1010b845: add      eax, 0x5f0
0x1010b84a: ret      
0x1010b84b: int3     
0x1010b84c: int3     
0x1010b84d: int3     
0x1010b84e: int3     
0x1010b84f: int3     
0x1010b850: push     esi
0x1010b851: mov      esi, dword ptr [esp + 8]
0x1010b855: test     esi, esi
0x1010b857: je       0x1010b87d ; "^ÃÌ°ý6Ét&D$ÀtÙD$PD$ìÙ\$ÙD$Ù$PèRöÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ°ý6Ét6D$Àt.ÙD$PD$ìÙ\$ÙD$$Ù\$ÙD$ Ù\$ÙD$Ù$PèQköÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b859: mov      eax, dword ptr [0x1036fca8]
0x1010b85e: add      eax, 0x5b0
0x1010b863: push     eax
0x1010b864: push     eax
0x1010b865: push     0x102d4104 ; "map/%s/%s.map"
0x1010b86a: push     0x10585918
0x1010b86f: call     0x10263225 ; "Uìì S3Û9]uèD"
0x1010b874: add      esp, 0x10
0x1010b877: mov      dword ptr [esi], 0x10585918
0x1010b87d: pop      esi
0x1010b87e: ret      
0x1010b87f: int3     
0x1010b880: mov      ecx, dword ptr [0x1036fdb0]
0x1010b886: test     ecx, ecx
0x1010b888: je       0x1010b8b0 ; "ÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ°ý6Ét6D$Àt.ÙD$PD$ìÙ\$ÙD$$Ù\$ÙD$ Ù\$ÙD$Ù$PèQköÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b88a: mov      eax, dword ptr [esp + 0x10]
0x1010b88e: test     eax, eax
0x1010b890: je       0x1010b8b0 ; "ÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ°ý6Ét6D$Àt.ÙD$PD$ìÙ\$ÙD$$Ù\$ÙD$ Ù\$ÙD$Ù$PèQköÿÃÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b892: fld      dword ptr [esp + 0xc]
0x1010b896: push     eax
0x1010b897: mov      eax, dword ptr [esp + 8]
0x1010b89b: sub      esp, 8
0x1010b89e: fstp     dword ptr [esp + 4]
0x1010b8a2: fld      dword ptr [esp + 0x14]
0x1010b8a6: fstp     dword ptr [esp]
0x1010b8a9: push     eax
0x1010b8aa: call     0x10070ab0 ; "jÿhþ"+d¡"
0x1010b8af: ret      
0x1010b8b0: or       eax, 0xffffffff
0x1010b8b3: ret      
0x1010b8b4: int3     
0x1010b8b5: int3     
0x1010b8b6: int3     
0x1010b8b7: int3     
0x1010b8b8: int3     
0x1010b8b9: int3     
0x1010b8ba: int3     
0x1010b8bb: int3     
0x1010b8bc: int3     
0x1010b8bd: int3     
0x1010b8be: int3     
0x1010b8bf: int3     
0x1010b8c0: mov      ecx, dword ptr [0x1036fdb0]
0x1010b8c6: test     ecx, ecx
0x1010b8c8: je       0x1010b900 ; "ÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b8ca: mov      eax, dword ptr [esp + 0x18]
0x1010b8ce: test     eax, eax
0x1010b8d0: je       0x1010b900 ; "ÈÿÃÌÌÌÌÌÌÌÌÌÌÌÌ¡°ý6ìÀtH¬"
0x1010b8d2: fld      dword ptr [esp + 0x14]
0x1010b8d6: push     eax
0x1010b8d7: mov      eax, dword ptr [esp + 8]
0x1010b8db: sub      esp, 0x10
0x1010b8de: fstp     dword ptr [esp + 0xc]
0x1010b8e2: fld      dword ptr [esp + 0x24]
0x1010b8e6: fstp     dword ptr [esp + 8]
0x1010b8ea: fld      dword ptr [esp + 0x20]
0x1010b8ee: fstp     dword ptr [esp + 4]
0x1010b8f2: fld      dword ptr [esp + 0x1c]
0x1010b8f6: fstp     dword ptr [esp]
0x1010b8f9: push     eax
0x1010b8fa: call     0x10072450 ; "jÿh%+d¡"
0x1010b8ff: ret      
0x1010b900: or       eax, 0xffffffff
0x1010b903: ret      
0x1010b904: int3     
0x1010b905: int3     
0x1010b906: int3     
0x1010b907: int3     
0x1010b908: int3     
0x1010b909: int3     
0x1010b90a: int3     
0x1010b90b: int3     
0x1010b90c: int3     
0x1010b90d: int3     
0x1010b90e: int3     
0x1010b90f: int3     
0x1010b910: mov      eax, dword ptr [0x1036fdb0]
0x1010b915: sub      esp, 0xc
0x1010b918: test     eax, eax
0x1010b91a: je       0x1010b964 ; "D$L$Ç"
0x1010b91c: mov      ecx, dword ptr [eax + 0x1aac]
0x1010b922: test     ecx, ecx
0x1010b924: je       0x1010b939 ; "Ù$ÝHí,ÜÉÙÉèåz"
0x1010b926: mov      edx, dword ptr [esp + 0x14]
0x1010b92a: lea      eax, [esp]
0x1010b92d: push     eax
0x1010b92e: mov      eax, dword ptr [esp + 0x14]
0x1010b932: push     edx
0x1010b933: push     eax
0x1010b934: call     0x1013bcc0 ; "ì"
0x1010b939: fld      dword ptr [esp]
0x1010b93c: fld      qword ptr [0x102ced48]
0x1010b942: fmul     st(1), st(0)
0x1010b944: fxch     st(1)
0x1010b946: call     0x10263430
0x1010b94b: fmul     dword ptr [esp + 4]
0x1010b94f: mov      ecx, dword ptr [esp + 0x18]
0x1010b953: mov      dword ptr [ecx], eax
0x1010b955: call     0x10263430
0x1010b95a: mov      edx, dword ptr [esp + 0x1c]
0x1010b95e: mov      dword ptr [edx], eax
0x1010b960: add      esp, 0xc
0x1010b963: ret      
0x1010b964: mov      eax, dword ptr [esp + 0x18]
0x1010b968: mov      ecx, dword ptr [esp + 0x1c]
0x1010b96c: mov      dword ptr [eax], 0
0x1010b972: mov      dword ptr [ecx], 0
0x1010b978: add      esp, 0xc
0x1010b97b: ret      
0x1010b97c: int3     
0x1010b97d: int3     
0x1010b97e: int3     
0x1010b97f: int3     
0x1010b980: sub      esp, 0x104
0x1010b986: mov      eax, dword ptr [0x10367584]
0x1010b98b: xor      eax, esp
0x1010b98d: mov      dword ptr [esp + 0x100], eax
0x1010b994: mov      eax, dword ptr [esp + 0x118]
