package eu.javiertorres.argame;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.graphics.PixelFormat;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup.LayoutParams;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.Toast;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.backends.android.AndroidApplication;
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration;

import org.artoolkit.ar.base.ARToolKit;
import org.artoolkit.ar.base.AndroidUtils;
import org.artoolkit.ar.base.assets.AssetHelper;
import org.artoolkit.ar.base.camera.CameraEventListener;
import org.artoolkit.ar.base.camera.CameraPreferencesActivity;
import org.artoolkit.ar.base.camera.CaptureCameraPreview;

public class AndroidLauncher extends AndroidApplication implements CameraEventListener {
	protected final static String TAG = "ARActivity";

	private View glView;
	protected FrameLayout mainLayout; 
	protected int pattSize = 16;
	protected int pattCountMax = 25;
	private boolean firstUpdate = false;
	private boolean firstRender = false;
	private ARGame arGame;
	
	@Override
	protected void onCreate (Bundle savedInstanceState) {
        Log.i(TAG, "onCreate()");
		super.onCreate(savedInstanceState);
		AndroidApplicationConfiguration config = new AndroidApplicationConfiguration();
		
        // we need to change the default pixel format - since it does not include an alpha channel 
        // we need the alpha channel so the camera preview will be seen behind the GL scene
		config.useGLSurfaceView20API18 = false;
		config.r = 8;
		config.g = 8;
		config.b = 8;
		config.a = 8;
		
		//Disable unneeded input devices
		config.useAccelerometer = false;
		config.useCompass = false;
		
		arGame = new ARGame();
		glView = initializeForView(arGame, config);

		//
		// ARToolkit initialization
		//
        // This needs to be done just only the very first time the application is run,
        // or whenever a new preference is added (e.g. after an application upgrade).
        PreferenceManager.setDefaultValues(this, R.xml.preferences, false);
		PreferenceManager.setDefaultValues(this, org.artoolkit.ar.base.R.xml.preferences, false);
        
        getWindow().setFormat(PixelFormat.TRANSLUCENT);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);

        setContentView(R.layout.main);
        AndroidUtils.reportDisplayInformation(this);
        
		AssetHelper assetHelper = new AssetHelper(getAssets());        
		assetHelper.cacheAssetFolder(this, "Data");
	}
	
	@Override
    protected void onStart() {
		//Log.i(TAG, "onStart()");
    	super.onStart();    

    	Log.i(TAG, "Activity starting.");

		// Initialize ARToolKit. Use cache directory for Data files.
    	if (!ARToolKit.getInstance().initialiseNativeWithOptions(this.getCacheDir().getAbsolutePath(), pattSize, pattCountMax)) {
        	
    		 new AlertDialog.Builder(this)
    	      .setMessage("The native library is not loaded. The application cannot continue.")
    	      .setTitle("Error")
    	      .setCancelable(true)
    	      .setNeutralButton(android.R.string.cancel,
    	         new DialogInterface.OnClickListener() {
    	         public void onClick(DialogInterface dialog, int whichButton){ finish(); }    	         
    	         })
    	      .show();

    		return;
        }    		
    	
    	mainLayout = (FrameLayout)this.findViewById(R.id.mainLayout);
    }
	
	@Override
    public void onResume() {
    	Log.i(TAG, "onResume()");
    	super.onResume();
    	
    	// Create the camera preview
    	CaptureCameraPreview ARPreview = new CaptureCameraPreview(this, this);
    	
    	Log.i(TAG, "CaptureCameraPreview created"); 
    	
    	// Create the GL view
		((GLSurfaceView)glView).getHolder().setFormat(PixelFormat.TRANSLUCENT); // Needs to be a translucent surface so the camera preview shows through.
		((GLSurfaceView)glView).setZOrderMediaOverlay(true); // Request that GL view's SurfaceView be on top of other SurfaceViews (including CameraPreview's SurfaceView).

		Log.i(TAG, "GLSurfaceView created");
		
		// Add the views to the interface
        mainLayout.addView(ARPreview, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT));
        mainLayout.addView(glView, new LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT));

		Log.i(TAG, "Views added to main layout.");
    }

	@Override
	public void cameraPreviewStarted(int width, int height, int rate, int cameraIndex, boolean cameraIsFrontFacing) {
		if (ARToolKit.getInstance().initialiseAR(width, height, "Data/camera_para.dat", cameraIndex, cameraIsFrontFacing)) { // Expects Data to be already in the cache dir. This can be done with the AssetUnpacker.
			Log.i(TAG, "Camera initialised");
		} else {
			// Error
			Log.e(TAG, "Error initialising camera. Cannot continue.");
			finish();
		}
		
		Toast.makeText(this, "Camera settings: " + width + "x" + height + "@" + rate + "fps", Toast.LENGTH_SHORT).show();
		
		firstUpdate = true;
		firstRender = true;
		
	}

	@Override
	public void cameraPreviewFrame(byte[] frame) {
		if (firstUpdate) {
			// ARToolKit has been initialised. The renderer can now add markers, etc...
			arGame.initDetection();
			firstUpdate = false;
		}
		
		if (ARToolKit.getInstance().convertAndDetect(frame)) {
			if (firstRender) {
				arGame.initRender();
				firstRender = false;
			}
			Gdx.graphics.requestRendering();
		}			
	}

	@Override
	public void cameraPreviewStopped() {
		ARToolKit.getInstance().cleanup();
	}

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        startActivity(new Intent(this, CameraPreferencesActivity.class));
        return true;
    }
}
