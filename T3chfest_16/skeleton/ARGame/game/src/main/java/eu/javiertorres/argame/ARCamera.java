package eu.javiertorres.argame;

import com.badlogic.gdx.graphics.Camera;
import com.badlogic.gdx.math.Matrix4;

import org.artoolkit.ar.base.ARToolKit;

public class ARCamera extends Camera {
	public ARCamera() {
		update(true);
	}

	@Override
	public void update () {
		update(true);
	}

	@Override
	public void update (boolean updateFrustum) {
		// Use the same camera as ARToolkit
		projection.set(ARToolKit.getInstance().getProjectionMatrix());
		combined.set(projection);

		if (updateFrustum) {
			invProjectionView.set(combined);
			Matrix4.inv(invProjectionView.val);
			frustum.update(invProjectionView);
		}
	}

}
