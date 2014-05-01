
function init_php_file_tree() {
	if (!document.getElementsByTagName) return;
	
	var aMenus = document.getElementsByTagName("LI");
	for (var i = 0; i < aMenus.length; i++) {
		var mclass = aMenus[i].className;
		if (mclass.indexOf("pft-directory") > -1) {
			var submenu = aMenus[i].childNodes;
			for (var j = 0; j < submenu.length; j++) {
				if (submenu[j].tagName == "A") {
					
					submenu[j].onclick = function() {
						var node = this.nextSibling;
											
						while (1) {
							if (node != null) {
								if (node.tagName == "UL") {
									var d = (node.style.display == "none")
									node.style.display = (d) ? "block" : "none";
									this.className = (d) ? "open" : "closed";
									return false;
								}
								node = node.nextSibling;
							} else {
								return false;
							}
						}
						return false;
					}
					
					submenu[j].className = (mclass.indexOf("open") > -1) ? "open" : "closed";
				}
				
				if (submenu[j].tagName == "UL")
					submenu[j].style.display = (mclass.indexOf("open") > -1) ? "block" : "none";
			}
		}
	}
	return false;
}

window.onload = init_php_file_tree;