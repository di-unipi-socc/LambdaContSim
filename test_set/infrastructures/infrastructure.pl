node(cloud1, cloudProvider, [pubKeyE,antiTamp], [js,py3,numPy], (inf, inf, inf)).
node(cloud2, cloudProvider, [pubKeyE,antiTamp], [js,py3,numPy], (inf, inf, inf)).
node(cloud3, cloudProvider, [pubKeyE,antiTamp], [js,py3,numPy], (inf, inf, inf)).
node(cloud4, cloudProvider, [pubKeyE,antiTamp], [js,py3,numPy], (inf, inf, inf)).
node(cloud5, cloudProvider, [pubKeyE,antiTamp], [js,py3,numPy], (inf, inf, inf)).
node(fog1, telco, [pubKeyE], [py3,numPy], (2048, 4, 1500)).
node(fog2, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog3, university, [], [py3], (1024, 2, 1000)).
node(fog4, telco, [pubKeyE,antiTamp], [js,py3], (2048, 4, 1500)).
node(fog5, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog6, telco, [pubKeyE], [py3,numPy], (2048, 4, 1500)).
node(fog7, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(fog8, university, [], [py3], (1024, 2, 1000)).
node(fog9, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog10, university, [], [py3], (1024, 2, 1000)).
node(fog11, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(fog12, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog13, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog14, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog15, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog16, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog17, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog18, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog19, telco, [pubKeyE,antiTamp], [js,py3], (3500, 16, 2000)).
node(fog20, university, [pubKeyE,antiTamp], [py3,numPy], (4096, 4, 2000)).
node(fog21, telco, [pubKeyE], [py3,numPy], (2048, 4, 1500)).
node(fog22, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(fog23, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(fog24, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(fog25, university, [pubKeyE], [js,py3], (2048, 2, 2000)).
node(edge1, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge2, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge3, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge4, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge5, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge6, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge7, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge8, privateCitizen2, [pubKeyE], [py3], (512, 2, 1500)).
node(edge9, privateCitizen1, [], [js], (1024, 4, 2500)).
node(edge10, privateCitizen1, [], [js], (1024, 4, 2500)).
eventGenerator(userDevice, fog1).
eventGenerator(userDevice, fog6).
eventGenerator(userDevice, fog10).
eventGenerator(userDevice, fog15).
eventGenerator(userDevice, fog18).
eventGenerator(userDevice, fog19).
eventGenerator(userDevice, fog23).
eventGenerator(userDevice, fog25).
service(cMaps, cloudProvider, maps, cloud1).
service(cMaps, cloudProvider, maps, cloud2).
service(cMaps, cloudProvider, maps, cloud3).
service(cMaps, cloudProvider, maps, cloud4).
service(myUserDb, appOp, userDB, fog2).
service(rules, pa, checkRules, fog2).
service(myUserDb, appOp, userDB, fog3).
service(myUserDb, appOp, userDB, fog4).
service(gp, pa, checkGp, fog4).
service(myUserDb, appOp, userDB, fog5).
service(rules, pa, checkRules, fog5).
service(myUserDb, appOp, userDB, fog6).
service(gp, pa, checkGp, fog6).
service(rules, pa, checkRules, fog6).
service(gp, pa, checkGp, fog7).
service(myUserDb, appOp, userDB, fog8).
service(gp, pa, checkGp, fog8).
service(gp, pa, checkGp, fog10).
service(rules, pa, checkRules, fog10).
service(gp, pa, checkGp, fog11).
service(rules, pa, checkRules, fog11).
service(myUserDb, appOp, userDB, fog12).
service(gp, pa, checkGp, fog12).
service(rules, pa, checkRules, fog12).
service(rules, pa, checkRules, fog13).
service(myUserDb, appOp, userDB, fog14).
service(rules, pa, checkRules, fog14).
service(gp, pa, checkGp, fog15).
service(rules, pa, checkRules, fog15).
service(rules, pa, checkRules, fog16).
service(gp, pa, checkGp, fog17).
service(rules, pa, checkRules, fog17).
service(myUserDb, appOp, userDB, fog18).
service(gp, pa, checkGp, fog18).
service(myUserDb, appOp, userDB, fog19).
service(gp, pa, checkGp, fog19).
service(myUserDb, appOp, userDB, fog20).
service(rules, pa, checkRules, fog20).
service(gp, pa, checkGp, fog21).
service(myUserDb, appOp, userDB, fog22).
service(gp, pa, checkGp, fog22).
service(rules, pa, checkRules, fog22).
service(myUserDb, appOp, userDB, fog24).
service(gp, pa, checkGp, fog24).
service(rules, pa, checkRules, fog24).
service(myUserDb, appOp, userDB, fog25).
service(gp, pa, checkGp, fog25).
service(openM, openS, maps, edge1).
service(openM, openS, maps, edge4).
service(openM, openS, maps, edge6).
service(openM, openS, maps, edge7).
service(openM, openS, maps, edge8).
service(openM, openS, maps, edge9).
service(openM, openS, maps, edge10).
link(X,X,0).
link(X,Y,L) :- dif(X,Y), (latency(X,Y,L);latency(Y,X,L)).
latency(cloud1, cloud2, 54).
latency(cloud1, cloud3, 45).
latency(cloud1, cloud4, 46).
latency(cloud1, cloud5, 55).
latency(cloud1, fog1, 37).
latency(cloud1, fog2, 41).
latency(cloud1, fog3, 38).
latency(cloud1, fog4, 36).
latency(cloud1, fog5, 34).
latency(cloud1, fog6, 39).
latency(cloud1, fog7, 36).
latency(cloud1, fog8, 35).
latency(cloud1, fog9, 30).
latency(cloud1, fog10, 38).
latency(cloud1, fog11, 36).
latency(cloud1, fog12, 41).
latency(cloud1, fog13, 37).
latency(cloud1, fog14, 37).
latency(cloud1, fog15, 32).
latency(cloud1, fog16, 31).
latency(cloud1, fog17, 33).
latency(cloud1, fog18, 37).
latency(cloud1, fog19, 31).
latency(cloud1, fog20, 33).
latency(cloud1, fog21, 33).
latency(cloud1, fog22, 38).
latency(cloud1, fog23, 40).
latency(cloud1, fog24, 35).
latency(cloud1, fog25, 36).
latency(cloud1, edge1, 38).
latency(cloud1, edge2, 39).
latency(cloud1, edge3, 38).
latency(cloud1, edge4, 37).
latency(cloud1, edge5, 38).
latency(cloud1, edge6, 39).
latency(cloud1, edge7, 39).
latency(cloud1, edge8, 40).
latency(cloud1, edge9, 38).
latency(cloud1, edge10, 40).
latency(cloud2, cloud3, 52).
latency(cloud2, cloud4, 42).
latency(cloud2, cloud5, 55).
latency(cloud2, fog1, 36).
latency(cloud2, fog2, 32).
latency(cloud2, fog3, 35).
latency(cloud2, fog4, 35).
latency(cloud2, fog5, 36).
latency(cloud2, fog6, 37).
latency(cloud2, fog7, 33).
latency(cloud2, fog8, 38).
latency(cloud2, fog9, 38).
latency(cloud2, fog10, 39).
latency(cloud2, fog11, 35).
latency(cloud2, fog12, 42).
latency(cloud2, fog13, 36).
latency(cloud2, fog14, 33).
latency(cloud2, fog15, 40).
latency(cloud2, fog16, 41).
latency(cloud2, fog17, 36).
latency(cloud2, fog18, 40).
latency(cloud2, fog19, 30).
latency(cloud2, fog20, 40).
latency(cloud2, fog21, 35).
latency(cloud2, fog22, 39).
latency(cloud2, fog23, 33).
latency(cloud2, fog24, 40).
latency(cloud2, fog25, 30).
latency(cloud2, edge1, 35).
latency(cloud2, edge2, 36).
latency(cloud2, edge3, 37).
latency(cloud2, edge4, 36).
latency(cloud2, edge5, 37).
latency(cloud2, edge6, 38).
latency(cloud2, edge7, 39).
latency(cloud2, edge8, 37).
latency(cloud2, edge9, 38).
latency(cloud2, edge10, 38).
latency(cloud3, cloud4, 33).
latency(cloud3, cloud5, 51).
latency(cloud3, fog1, 32).
latency(cloud3, fog2, 35).
latency(cloud3, fog3, 32).
latency(cloud3, fog4, 36).
latency(cloud3, fog5, 38).
latency(cloud3, fog6, 34).
latency(cloud3, fog7, 38).
latency(cloud3, fog8, 36).
latency(cloud3, fog9, 40).
latency(cloud3, fog10, 33).
latency(cloud3, fog11, 40).
latency(cloud3, fog12, 33).
latency(cloud3, fog13, 38).
latency(cloud3, fog14, 40).
latency(cloud3, fog15, 36).
latency(cloud3, fog16, 38).
latency(cloud3, fog17, 38).
latency(cloud3, fog18, 31).
latency(cloud3, fog19, 37).
latency(cloud3, fog20, 33).
latency(cloud3, fog21, 38).
latency(cloud3, fog22, 34).
latency(cloud3, fog23, 32).
latency(cloud3, fog24, 38).
latency(cloud3, fog25, 33).
latency(cloud3, edge1, 38).
latency(cloud3, edge2, 39).
latency(cloud3, edge3, 39).
latency(cloud3, edge4, 41).
latency(cloud3, edge5, 40).
latency(cloud3, edge6, 41).
latency(cloud3, edge7, 40).
latency(cloud3, edge8, 37).
latency(cloud3, edge9, 37).
latency(cloud3, edge10, 37).
latency(cloud4, cloud5, 53).
latency(cloud4, fog1, 41).
latency(cloud4, fog2, 33).
latency(cloud4, fog3, 30).
latency(cloud4, fog4, 38).
latency(cloud4, fog5, 40).
latency(cloud4, fog6, 35).
latency(cloud4, fog7, 30).
latency(cloud4, fog8, 32).
latency(cloud4, fog9, 37).
latency(cloud4, fog10, 37).
latency(cloud4, fog11, 30).
latency(cloud4, fog12, 36).
latency(cloud4, fog13, 36).
latency(cloud4, fog14, 39).
latency(cloud4, fog15, 35).
latency(cloud4, fog16, 37).
latency(cloud4, fog17, 32).
latency(cloud4, fog18, 33).
latency(cloud4, fog19, 35).
latency(cloud4, fog20, 37).
latency(cloud4, fog21, 33).
latency(cloud4, fog22, 32).
latency(cloud4, fog23, 35).
latency(cloud4, fog24, 41).
latency(cloud4, fog25, 38).
latency(cloud4, edge1, 40).
latency(cloud4, edge2, 39).
latency(cloud4, edge3, 38).
latency(cloud4, edge4, 40).
latency(cloud4, edge5, 35).
latency(cloud4, edge6, 38).
latency(cloud4, edge7, 39).
latency(cloud4, edge8, 39).
latency(cloud4, edge9, 36).
latency(cloud4, edge10, 39).
latency(cloud5, fog1, 39).
latency(cloud5, fog2, 32).
latency(cloud5, fog3, 37).
latency(cloud5, fog4, 35).
latency(cloud5, fog5, 38).
latency(cloud5, fog6, 37).
latency(cloud5, fog7, 40).
latency(cloud5, fog8, 40).
latency(cloud5, fog9, 36).
latency(cloud5, fog10, 31).
latency(cloud5, fog11, 32).
latency(cloud5, fog12, 34).
latency(cloud5, fog13, 30).
latency(cloud5, fog14, 39).
latency(cloud5, fog15, 37).
latency(cloud5, fog16, 38).
latency(cloud5, fog17, 36).
latency(cloud5, fog18, 37).
latency(cloud5, fog19, 33).
latency(cloud5, fog20, 35).
latency(cloud5, fog21, 30).
latency(cloud5, fog22, 32).
latency(cloud5, fog23, 33).
latency(cloud5, fog24, 32).
latency(cloud5, fog25, 40).
latency(cloud5, edge1, 37).
latency(cloud5, edge2, 36).
latency(cloud5, edge3, 37).
latency(cloud5, edge4, 38).
latency(cloud5, edge5, 37).
latency(cloud5, edge6, 38).
latency(cloud5, edge7, 38).
latency(cloud5, edge8, 39).
latency(cloud5, edge9, 35).
latency(cloud5, edge10, 38).
latency(fog1, fog2, 11).
latency(fog1, fog3, 18).
latency(fog1, fog4, 11).
latency(fog1, fog5, 12).
latency(fog1, fog6, 14).
latency(fog1, fog7, 13).
latency(fog1, fog8, 14).
latency(fog1, fog9, 19).
latency(fog1, fog10, 14).
latency(fog1, fog11, 11).
latency(fog1, fog12, 18).
latency(fog1, fog13, 12).
latency(fog1, fog14, 8).
latency(fog1, fog15, 14).
latency(fog1, fog16, 7).
latency(fog1, fog17, 12).
latency(fog1, fog18, 13).
latency(fog1, fog19, 6).
latency(fog1, fog20, 13).
latency(fog1, fog21, 11).
latency(fog1, fog22, 14).
latency(fog1, fog23, 11).
latency(fog1, fog24, 14).
latency(fog1, fog25, 14).
latency(fog1, edge1, 9).
latency(fog1, edge2, 12).
latency(fog1, edge3, 7).
latency(fog1, edge4, 10).
latency(fog1, edge5, 10).
latency(fog1, edge6, 10).
latency(fog1, edge7, 14).
latency(fog1, edge8, 7).
latency(fog1, edge9, 7).
latency(fog1, edge10, 11).
latency(fog2, fog3, 14).
latency(fog2, fog4, 7).
latency(fog2, fog5, 10).
latency(fog2, fog6, 5).
latency(fog2, fog7, 10).
latency(fog2, fog8, 11).
latency(fog2, fog9, 15).
latency(fog2, fog10, 14).
latency(fog2, fog11, 6).
latency(fog2, fog12, 13).
latency(fog2, fog13, 12).
latency(fog2, fog14, 9).
latency(fog2, fog15, 9).
latency(fog2, fog16, 13).
latency(fog2, fog17, 11).
latency(fog2, fog18, 8).
latency(fog2, fog19, 11).
latency(fog2, fog20, 14).
latency(fog2, fog21, 12).
latency(fog2, fog22, 16).
latency(fog2, fog23, 10).
latency(fog2, fog24, 14).
latency(fog2, fog25, 9).
latency(fog2, edge1, 9).
latency(fog2, edge2, 10).
latency(fog2, edge3, 10).
latency(fog2, edge4, 8).
latency(fog2, edge5, 7).
latency(fog2, edge6, 6).
latency(fog2, edge7, 13).
latency(fog2, edge8, 11).
latency(fog2, edge9, 7).
latency(fog2, edge10, 10).
latency(fog3, fog4, 14).
latency(fog3, fog5, 11).
latency(fog3, fog6, 15).
latency(fog3, fog7, 15).
latency(fog3, fog8, 13).
latency(fog3, fog9, 8).
latency(fog3, fog10, 14).
latency(fog3, fog11, 13).
latency(fog3, fog12, 14).
latency(fog3, fog13, 7).
latency(fog3, fog14, 10).
latency(fog3, fog15, 9).
latency(fog3, fog16, 17).
latency(fog3, fog17, 17).
latency(fog3, fog18, 14).
latency(fog3, fog19, 13).
latency(fog3, fog20, 12).
latency(fog3, fog21, 12).
latency(fog3, fog22, 16).
latency(fog3, fog23, 15).
latency(fog3, fog24, 13).
latency(fog3, fog25, 19).
latency(fog3, edge1, 15).
latency(fog3, edge2, 13).
latency(fog3, edge3, 11).
latency(fog3, edge4, 15).
latency(fog3, edge5, 8).
latency(fog3, edge6, 15).
latency(fog3, edge7, 10).
latency(fog3, edge8, 14).
latency(fog3, edge9, 17).
latency(fog3, edge10, 18).
latency(fog4, fog5, 11).
latency(fog4, fog6, 8).
latency(fog4, fog7, 11).
latency(fog4, fog8, 12).
latency(fog4, fog9, 15).
latency(fog4, fog10, 7).
latency(fog4, fog11, 8).
latency(fog4, fog12, 15).
latency(fog4, fog13, 11).
latency(fog4, fog14, 11).
latency(fog4, fog15, 9).
latency(fog4, fog16, 12).
latency(fog4, fog17, 11).
latency(fog4, fog18, 5).
latency(fog4, fog19, 5).
latency(fog4, fog20, 14).
latency(fog4, fog21, 5).
latency(fog4, fog22, 10).
latency(fog4, fog23, 10).
latency(fog4, fog24, 12).
latency(fog4, fog25, 15).
latency(fog4, edge1, 10).
latency(fog4, edge2, 12).
latency(fog4, edge3, 12).
latency(fog4, edge4, 11).
latency(fog4, edge5, 12).
latency(fog4, edge6, 13).
latency(fog4, edge7, 12).
latency(fog4, edge8, 8).
latency(fog4, edge9, 5).
latency(fog4, edge10, 12).
latency(fog5, fog6, 5).
latency(fog5, fog7, 10).
latency(fog5, fog8, 9).
latency(fog5, fog9, 8).
latency(fog5, fog10, 11).
latency(fog5, fog11, 11).
latency(fog5, fog12, 15).
latency(fog5, fog13, 12).
latency(fog5, fog14, 12).
latency(fog5, fog15, 13).
latency(fog5, fog16, 13).
latency(fog5, fog17, 11).
latency(fog5, fog18, 12).
latency(fog5, fog19, 6).
latency(fog5, fog20, 10).
latency(fog5, fog21, 11).
latency(fog5, fog22, 15).
latency(fog5, fog23, 6).
latency(fog5, fog24, 6).
latency(fog5, fog25, 10).
latency(fog5, edge1, 5).
latency(fog5, edge2, 10).
latency(fog5, edge3, 9).
latency(fog5, edge4, 10).
latency(fog5, edge5, 9).
latency(fog5, edge6, 8).
latency(fog5, edge7, 7).
latency(fog5, edge8, 7).
latency(fog5, edge9, 11).
latency(fog5, edge10, 11).
latency(fog6, fog7, 5).
latency(fog6, fog8, 6).
latency(fog6, fog9, 11).
latency(fog6, fog10, 11).
latency(fog6, fog11, 6).
latency(fog6, fog12, 11).
latency(fog6, fog13, 11).
latency(fog6, fog14, 7).
latency(fog6, fog15, 11).
latency(fog6, fog16, 8).
latency(fog6, fog17, 6).
latency(fog6, fog18, 12).
latency(fog6, fog19, 11).
latency(fog6, fog20, 10).
latency(fog6, fog21, 12).
latency(fog6, fog22, 14).
latency(fog6, fog23, 11).
latency(fog6, fog24, 10).
latency(fog6, fog25, 10).
latency(fog6, edge1, 5).
latency(fog6, edge2, 5).
latency(fog6, edge3, 7).
latency(fog6, edge4, 7).
latency(fog6, edge5, 7).
latency(fog6, edge6, 8).
latency(fog6, edge7, 8).
latency(fog6, edge8, 7).
latency(fog6, edge9, 11).
latency(fog6, edge10, 11).
latency(fog7, fog8, 11).
latency(fog7, fog9, 13).
latency(fog7, fog10, 16).
latency(fog7, fog11, 9).
latency(fog7, fog12, 12).
latency(fog7, fog13, 15).
latency(fog7, fog14, 12).
latency(fog7, fog15, 14).
latency(fog7, fog16, 10).
latency(fog7, fog17, 5).
latency(fog7, fog18, 16).
latency(fog7, fog19, 11).
latency(fog7, fog20, 10).
latency(fog7, fog21, 11).
latency(fog7, fog22, 13).
latency(fog7, fog23, 11).
latency(fog7, fog24, 11).
latency(fog7, fog25, 11).
latency(fog7, edge1, 10).
latency(fog7, edge2, 9).
latency(fog7, edge3, 10).
latency(fog7, edge4, 11).
latency(fog7, edge5, 7).
latency(fog7, edge6, 13).
latency(fog7, edge7, 12).
latency(fog7, edge8, 12).
latency(fog7, edge9, 6).
latency(fog7, edge10, 9).
latency(fog8, fog9, 5).
latency(fog8, fog10, 14).
latency(fog8, fog11, 8).
latency(fog8, fog12, 15).
latency(fog8, fog13, 14).
latency(fog8, fog14, 13).
latency(fog8, fog15, 11).
latency(fog8, fog16, 7).
latency(fog8, fog17, 11).
latency(fog8, fog18, 7).
latency(fog8, fog19, 8).
latency(fog8, fog20, 13).
latency(fog8, fog21, 12).
latency(fog8, fog22, 14).
latency(fog8, fog23, 12).
latency(fog8, fog24, 10).
latency(fog8, fog25, 15).
latency(fog8, edge1, 11).
latency(fog8, edge2, 10).
latency(fog8, edge3, 13).
latency(fog8, edge4, 11).
latency(fog8, edge5, 11).
latency(fog8, edge6, 13).
latency(fog8, edge7, 7).
latency(fog8, edge8, 13).
latency(fog8, edge9, 7).
latency(fog8, edge10, 15).
latency(fog9, fog10, 10).
latency(fog9, fog11, 11).
latency(fog9, fog12, 14).
latency(fog9, fog13, 13).
latency(fog9, fog14, 17).
latency(fog9, fog15, 6).
latency(fog9, fog16, 12).
latency(fog9, fog17, 13).
latency(fog9, fog18, 11).
latency(fog9, fog19, 13).
latency(fog9, fog20, 8).
latency(fog9, fog21, 15).
latency(fog9, fog22, 10).
latency(fog9, fog23, 14).
latency(fog9, fog24, 5).
latency(fog9, fog25, 15).
latency(fog9, edge1, 10).
latency(fog9, edge2, 14).
latency(fog9, edge3, 13).
latency(fog9, edge4, 12).
latency(fog9, edge5, 15).
latency(fog9, edge6, 13).
latency(fog9, edge7, 12).
latency(fog9, edge8, 12).
latency(fog9, edge9, 12).
latency(fog9, edge10, 16).
latency(fog10, fog11, 14).
latency(fog10, fog12, 16).
latency(fog10, fog13, 14).
latency(fog10, fog14, 14).
latency(fog10, fog15, 12).
latency(fog10, fog16, 7).
latency(fog10, fog17, 12).
latency(fog10, fog18, 12).
latency(fog10, fog19, 12).
latency(fog10, fog20, 11).
latency(fog10, fog21, 10).
latency(fog10, fog22, 5).
latency(fog10, fog23, 14).
latency(fog10, fog24, 5).
latency(fog10, fog25, 11).
latency(fog10, edge1, 6).
latency(fog10, edge2, 11).
latency(fog10, edge3, 13).
latency(fog10, edge4, 9).
latency(fog10, edge5, 16).
latency(fog10, edge6, 9).
latency(fog10, edge7, 14).
latency(fog10, edge8, 8).
latency(fog10, edge9, 12).
latency(fog10, edge10, 10).
latency(fog11, fog12, 7).
latency(fog11, fog13, 6).
latency(fog11, fog14, 11).
latency(fog11, fog15, 5).
latency(fog11, fog16, 13).
latency(fog11, fog17, 11).
latency(fog11, fog18, 10).
latency(fog11, fog19, 5).
latency(fog11, fog20, 11).
latency(fog11, fog21, 10).
latency(fog11, fog22, 12).
latency(fog11, fog23, 10).
latency(fog11, fog24, 16).
latency(fog11, fog25, 15).
latency(fog11, edge1, 11).
latency(fog11, edge2, 11).
latency(fog11, edge3, 8).
latency(fog11, edge4, 10).
latency(fog11, edge5, 5).
latency(fog11, edge6, 8).
latency(fog11, edge7, 14).
latency(fog11, edge8, 13).
latency(fog11, edge9, 10).
latency(fog11, edge10, 11).
latency(fog12, fog13, 9).
latency(fog12, fog14, 18).
latency(fog12, fog15, 12).
latency(fog12, fog16, 13).
latency(fog12, fog17, 13).
latency(fog12, fog18, 17).
latency(fog12, fog19, 12).
latency(fog12, fog20, 14).
latency(fog12, fog21, 15).
latency(fog12, fog22, 13).
latency(fog12, fog23, 17).
latency(fog12, fog24, 15).
latency(fog12, fog25, 12).
latency(fog12, edge1, 10).
latency(fog12, edge2, 6).
latency(fog12, edge3, 15).
latency(fog12, edge4, 8).
latency(fog12, edge5, 12).
latency(fog12, edge6, 10).
latency(fog12, edge7, 8).
latency(fog12, edge8, 12).
latency(fog12, edge9, 16).
latency(fog12, edge10, 13).
latency(fog13, fog14, 12).
latency(fog13, fog15, 11).
latency(fog13, fog16, 10).
latency(fog13, fog17, 10).
latency(fog13, fog18, 15).
latency(fog13, fog19, 6).
latency(fog13, fog20, 5).
latency(fog13, fog21, 11).
latency(fog13, fog22, 12).
latency(fog13, fog23, 14).
latency(fog13, fog24, 13).
latency(fog13, fog25, 12).
latency(fog13, edge1, 8).
latency(fog13, edge2, 6).
latency(fog13, edge3, 11).
latency(fog13, edge4, 8).
latency(fog13, edge5, 11).
latency(fog13, edge6, 10).
latency(fog13, edge7, 9).
latency(fog13, edge8, 10).
latency(fog13, edge9, 14).
latency(fog13, edge10, 12).
latency(fog14, fog15, 16).
latency(fog14, fog16, 15).
latency(fog14, fog17, 12).
latency(fog14, fog18, 15).
latency(fog14, fog19, 6).
latency(fog14, fog20, 9).
latency(fog14, fog21, 11).
latency(fog14, fog22, 9).
latency(fog14, fog23, 13).
latency(fog14, fog24, 16).
latency(fog14, fog25, 16).
latency(fog14, edge1, 11).
latency(fog14, edge2, 12).
latency(fog14, edge3, 11).
latency(fog14, edge4, 12).
latency(fog14, edge5, 8).
latency(fog14, edge6, 14).
latency(fog14, edge7, 15).
latency(fog14, edge8, 9).
latency(fog14, edge9, 15).
latency(fog14, edge10, 13).
latency(fog15, fog16, 8).
latency(fog15, fog17, 13).
latency(fog15, fog18, 5).
latency(fog15, fog19, 10).
latency(fog15, fog20, 13).
latency(fog15, fog21, 12).
latency(fog15, fog22, 7).
latency(fog15, fog23, 12).
latency(fog15, fog24, 11).
latency(fog15, fog25, 10).
latency(fog15, edge1, 11).
latency(fog15, edge2, 8).
latency(fog15, edge3, 7).
latency(fog15, edge4, 6).
latency(fog15, edge5, 9).
latency(fog15, edge6, 8).
latency(fog15, edge7, 11).
latency(fog15, edge8, 11).
latency(fog15, edge9, 14).
latency(fog15, edge10, 12).
latency(fog16, fog17, 5).
latency(fog16, fog18, 7).
latency(fog16, fog19, 11).
latency(fog16, fog20, 10).
latency(fog16, fog21, 10).
latency(fog16, fog22, 9).
latency(fog16, fog23, 14).
latency(fog16, fog24, 10).
latency(fog16, fog25, 11).
latency(fog16, edge1, 11).
latency(fog16, edge2, 10).
latency(fog16, edge3, 12).
latency(fog16, edge4, 8).
latency(fog16, edge5, 14).
latency(fog16, edge6, 10).
latency(fog16, edge7, 13).
latency(fog16, edge8, 9).
latency(fog16, edge9, 11).
latency(fog16, edge10, 9).
latency(fog17, fog18, 11).
latency(fog17, fog19, 6).
latency(fog17, fog20, 5).
latency(fog17, fog21, 6).
latency(fog17, fog22, 8).
latency(fog17, fog23, 13).
latency(fog17, fog24, 15).
latency(fog17, fog25, 6).
latency(fog17, edge1, 10).
latency(fog17, edge2, 11).
latency(fog17, edge3, 7).
latency(fog17, edge4, 9).
latency(fog17, edge5, 9).
latency(fog17, edge6, 11).
latency(fog17, edge7, 12).
latency(fog17, edge8, 12).
latency(fog17, edge9, 8).
latency(fog17, edge10, 14).
latency(fog18, fog19, 10).
latency(fog18, fog20, 10).
latency(fog18, fog21, 7).
latency(fog18, fog22, 10).
latency(fog18, fog23, 7).
latency(fog18, fog24, 12).
latency(fog18, fog25, 12).
latency(fog18, edge1, 7).
latency(fog18, edge2, 13).
latency(fog18, edge3, 12).
latency(fog18, edge4, 11).
latency(fog18, edge5, 14).
latency(fog18, edge6, 10).
latency(fog18, edge7, 14).
latency(fog18, edge8, 6).
latency(fog18, edge9, 10).
latency(fog18, edge10, 10).
latency(fog19, fog20, 11).
latency(fog19, fog21, 5).
latency(fog19, fog22, 10).
latency(fog19, fog23, 12).
latency(fog19, fog24, 12).
latency(fog19, fog25, 12).
latency(fog19, edge1, 7).
latency(fog19, edge2, 8).
latency(fog19, edge3, 7).
latency(fog19, edge4, 6).
latency(fog19, edge5, 7).
latency(fog19, edge6, 8).
latency(fog19, edge7, 11).
latency(fog19, edge8, 9).
latency(fog19, edge9, 10).
latency(fog19, edge10, 12).
latency(fog20, fog21, 11).
latency(fog20, fog22, 13).
latency(fog20, fog23, 9).
latency(fog20, fog24, 10).
latency(fog20, fog25, 10).
latency(fog20, edge1, 5).
latency(fog20, edge2, 10).
latency(fog20, edge3, 6).
latency(fog20, edge4, 10).
latency(fog20, edge5, 8).
latency(fog20, edge6, 8).
latency(fog20, edge7, 7).
latency(fog20, edge8, 7).
latency(fog20, edge9, 9).
latency(fog20, edge10, 11).
latency(fog21, fog22, 5).
latency(fog21, fog23, 8).
latency(fog21, fog24, 14).
latency(fog21, fog25, 10).
latency(fog21, edge1, 12).
latency(fog21, edge2, 11).
latency(fog21, edge3, 7).
latency(fog21, edge4, 11).
latency(fog21, edge5, 10).
latency(fog21, edge6, 13).
latency(fog21, edge7, 8).
latency(fog21, edge8, 13).
latency(fog21, edge9, 5).
latency(fog21, edge10, 13).
latency(fog22, fog23, 13).
latency(fog22, fog24, 9).
latency(fog22, fog25, 14).
latency(fog22, edge1, 11).
latency(fog22, edge2, 11).
latency(fog22, edge3, 12).
latency(fog22, edge4, 13).
latency(fog22, edge5, 15).
latency(fog22, edge6, 14).
latency(fog22, edge7, 13).
latency(fog22, edge8, 13).
latency(fog22, edge9, 10).
latency(fog22, edge10, 12).
latency(fog23, fog24, 9).
latency(fog23, fog25, 13).
latency(fog23, edge1, 11).
latency(fog23, edge2, 13).
latency(fog23, edge3, 13).
latency(fog23, edge4, 11).
latency(fog23, edge5, 15).
latency(fog23, edge6, 9).
latency(fog23, edge7, 13).
latency(fog23, edge8, 9).
latency(fog23, edge9, 5).
latency(fog23, edge10, 5).
latency(fog24, fog25, 10).
latency(fog24, edge1, 5).
latency(fog24, edge2, 11).
latency(fog24, edge3, 14).
latency(fog24, edge4, 10).
latency(fog24, edge5, 15).
latency(fog24, edge6, 8).
latency(fog24, edge7, 13).
latency(fog24, edge8, 7).
latency(fog24, edge9, 14).
latency(fog24, edge10, 11).
latency(fog25, edge1, 5).
latency(fog25, edge2, 6).
latency(fog25, edge3, 8).
latency(fog25, edge4, 8).
latency(fog25, edge5, 11).
latency(fog25, edge6, 8).
latency(fog25, edge7, 9).
latency(fog25, edge8, 7).
latency(fog25, edge9, 14).
latency(fog25, edge10, 8).
latency(edge1, edge2, 6).
latency(edge1, edge3, 11).
latency(edge1, edge4, 5).
latency(edge1, edge5, 12).
latency(edge1, edge6, 3).
latency(edge1, edge7, 9).
latency(edge1, edge8, 2).
latency(edge1, edge9, 11).
latency(edge1, edge10, 6).
latency(edge2, edge3, 9).
latency(edge2, edge4, 2).
latency(edge2, edge5, 6).
latency(edge2, edge6, 4).
latency(edge2, edge7, 3).
latency(edge2, edge8, 8).
latency(edge2, edge9, 12).
latency(edge2, edge10, 8).
latency(edge3, edge4, 10).
latency(edge3, edge5, 3).
latency(edge3, edge6, 8).
latency(edge3, edge7, 12).
latency(edge3, edge8, 10).
latency(edge3, edge9, 12).
latency(edge3, edge10, 8).
latency(edge4, edge5, 8).
latency(edge4, edge6, 2).
latency(edge4, edge7, 5).
latency(edge4, edge8, 7).
latency(edge4, edge9, 10).
latency(edge4, edge10, 6).
latency(edge5, edge6, 10).
latency(edge5, edge7, 9).
latency(edge5, edge8, 10).
latency(edge5, edge9, 13).
latency(edge5, edge10, 11).
latency(edge6, edge7, 7).
latency(edge6, edge8, 5).
latency(edge6, edge9, 8).
latency(edge6, edge10, 4).
latency(edge7, edge8, 11).
latency(edge7, edge9, 13).
latency(edge7, edge10, 11).
latency(edge8, edge9, 9).
latency(edge8, edge10, 4).
latency(edge9, edge10, 8).
