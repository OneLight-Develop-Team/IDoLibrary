// default find function is hard to use!!!
// find element in the array,if found return its index,
// -1 if not found. just a simple version

int findArray(int array[]; int element)
{
    foreach(int idx; int val; array)
    {
        if(val==element)
            return idx;
    }
    return -1;    
}


struct RotateSystem{
	vector side={0,0,0};
	vector up={0,0,0};
	vector aim={0,0,0};
};


RotateSystem getPYR(vector aim){
	RotateSystem a;
	vector temp = {0,1,0};
	vector side = normalize(cross(aim, temp));
	vector up = normalize(cross(side, aim));
	a.side = side;
	a.up = up;
	a.aim = aim;
	return a;
}


matrix getTrans(vector aim){
	RatateSystem rot = getPYR(aim);
	matrix trans_mtx = maketransform(rot.aim, rot.up, @P);
	return trans_mtx;
}


vector getTrans(vector aim, int trs){
	matrix trans_mtx = getTrans(aim);
	if(trs==0){
		vector trans_component = cracktransform(0,0,0,@P,trans_mtx);
	}
	if(trs==1){
		vector trans_component = cracktransform(0,0,1,@P,trans_mtx);
	}
	if(trs==2){
		vector trans_component = cracktransform(0,0,2,@P,trans_mtx);
	}
	return trans_component;
}


vector4 getOrient(vector aim){
	matrix trans_mtx = getTrans(aim);
	vector4 orient = quaternion(trans_mtx);
	return orient;
}


// primitive divider
// Run over primitives
void primDivider(){
	vector orig = primuv(0, "P", @primnum, {0,0,0});
	//vector v = primuv(0, "P", @primnum, {1,0,0});
	//vector u= primuv(0, "P", @primnum, {0,1,0});
	float vLength = chf("uSize");//distance(orig, u);
	float uLength = chf("vSize");//distance(orig, v);
	float seed = chf("seed");

	void addPointFromPos(int prim; vector pos; int thisLastPoints[]) {
		int newPoint = addpoint(geoself(), pos);
		append(thisLastPoints, newPoint);
		addvertex(geoself(), prim, newPoint);
	}

	void addPointFromPoint(int prim, lastPoint; int thisLastPoints[]) {
		int newPoint = addpoint(0, lastPoint);
		removepoint(0, lastPoint);
		append(thisLastPoints, newPoint);
		addvertex(geoself(), prim, newPoint);
	}

	float break_U(int primnum; int lastPoints[], lastPrims[]; float uPos, seed, uLength, vLength; float lastVpos[]) {
		int thisLastPrims[];
		float thisVPos[];
		int thisLastPoints[];
		vector uvPos_1;
		uvPos_1.y = uPos;
		vector uvPos_2;
		uPos += fit(rand((uPos+1+primnum)+seed),0,1, uLength, uLength*2);
		if(uPos > 1-(uLength)/2) {
			uPos = 1;
		}
		uvPos_2.y = uPos;
		float vPos = 0;
		while(vPos < 1) {
			vector pointPositions[] = vector[](array(4));
			int newPrim = addprim(0, "poly");
			append(thisLastPrims, newPrim);
			uvPos_1.x = vPos;
			uvPos_2.x = vPos;
			
			pointPositions[0] = primuv(0, "P", primnum, uvPos_1);
			pointPositions[1] = primuv(0, "P", primnum, uvPos_2);
			
			float startVPos = vPos;
			vPos += fit(rand((vPos+uPos+1+primnum)),0,1,vLength,vLength*2);
			
			if(vPos > 1-(vLength)/2) {
				vPos = 1;
			}
			int collapsed = 0;
			int savedLastPoints[] = int[](array(4));
			for(int i = 0; i < len(lastVpos); i++) {
				if(abs(vPos-lastVpos[i]) < chf("collRad")) {
					vPos = lastVpos[i];
					if(startVPos == lastVpos[i-1] || (startVPos == 0 && i-1 < 0)) {
						if(lastPrims[i] != 0) {
							removeprim(0, lastPrims[i], 0);
						}
						removepoint(0, lastPoints[i*4+1]);
						removepoint(0, lastPoints[i*4+2]);
						collapsed = 1;
						savedLastPoints[0] = lastPoints[i*4];
						savedLastPoints[3] = lastPoints[i*4+3];
						break;
					}
				}
			}
			
			vector uvPos_4 = uvPos_1;
			uvPos_4.x = vPos;
			vector uvPos_3 = uvPos_2;
			uvPos_3.x = vPos;
			pointPositions[2] = primuv(0, "P", primnum, uvPos_3);
			pointPositions[3] = primuv(0, "P", primnum, uvPos_4);
			
			for(int i = 0; i < len(pointPositions); i++) {
				if(collapsed == 0 || i == 1 || i == 2) {
					addPointFromPos(newPrim, pointPositions[i], thisLastPoints);
				} else {
					addPointFromPoint(newPrim, savedLastPoints[i], thisLastPoints);
				}
			}
			
			if(chi("groupCollapsed") == 1) {
				setprimgroup(0, "collapsed", newPrim, collapsed, "set");
			}
			append(thisVPos, vPos);
		}
		
		lastPoints = thisLastPoints;
		lastVpos = thisVPos;
		lastPrims = thisLastPrims;
		return uPos;
	}

	float uPos = 0;
	float lastVpos[];
	int lastPrims[];
	int lastPoints[];
	while(uPos < 1) {
		uPos = break_U(@primnum, lastPoints, lastPrims, uPos, seed, uLength, vLength, lastVpos);
	}
	removeprim(0, @primnum, 1);
}