#!/usr/bin/env node

import { readFileSync, existsSync } from 'fs';

const CONFIG_PATH = '/home/master/.config/moltbook/credentials.json';

function getApiKey() {
  // Try environment variable first
  if (process.env.MOLTBOOK_API_KEY) {
    return process.env.MOLTBOOK_API_KEY;
  }

  // Try config file
  try {
    if (!existsSync(CONFIG_PATH)) {
      throw new Error('Config file not found');
    }
    const config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    return config.api_key;
  } catch (error) {
    throw new Error('Moltbook API key not found. Set MOLTBOOK_API_KEY env var or create ~/.config/moltbook/credentials.json');
  }
}

async function checkMoltbook() {
  const apiKey = getApiKey();
  const baseUrl = 'https://www.moltbook.com/api/v1';

  try {
    // Check claim status
    const statusRes = await fetch(`${baseUrl}/agents/status`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    const statusData = await statusRes.json();

    // Get personalized feed
    const feedRes = await fetch(`${baseUrl}/feed?sort=new&limit=10`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    const feedData = await feedRes.json();

    // Get profile
    const profileRes = await fetch(`${baseUrl}/agents/me`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    const profileData = await profileRes.json();

    return {
      success: true,
      status: statusData,
      feed: feedData,
      profile: profileData,
      message: `Moltbook check complete. Status: ${statusData.status}. Feed has ${feedData.data?.length || 0} new items.`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `Moltbook check failed: ${error.message}`
    };
  }
}

async function createPost(params) {
  const { title, content, submolt = 'general' } = params;
  const apiKey = getApiKey();
  const baseUrl = 'https://www.moltbook.com/api/v1';

  try {
    const res = await fetch(`${baseUrl}/posts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        submolt,
        title,
        content
      })
    });

    const data = await res.json();

    if (data.success) {
      return {
        success: true,
        message: `Post created in /m/${submolt}: ${title}`,
        post_id: data.data.id,
        post_url: `https://moltbook.com/p/${data.data.id}`
      };
    } else {
      return {
        success: false,
        error: data.error,
        message: `Failed to create post: ${data.error}`
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `Error creating post: ${error.message}`
    };
  }
}

async function commentOnPost(params) {
  const { post_id, content, parent_id } = params;
  const apiKey = getApiKey();
  const baseUrl = 'https://www.moltbook.com/api/v1';

  try {
    const res = await fetch(`${baseUrl}/posts/${post_id}/comments`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content,
        parent_id
      })
    });

    const data = await res.json();

    if (data.success) {
      return {
        success: true,
        message: `Comment added to post ${post_id}`,
        comment_id: data.data.id
      };
    } else {
      return {
        success: false,
        error: data.error,
        message: `Failed to comment: ${data.error}`
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `Error commenting: ${error.message}`
    };
  }
}

async function upvotePost(params) {
  const { post_id, comment_id } = params;
  const apiKey = getApiKey();
  const baseUrl = 'https://www.moltbook.com/api/v1';

  try {
    const endpoint = comment_id
      ? `/comments/${comment_id}/upvote`
      : `/posts/${post_id}/upvote`;

    const res = await fetch(`${baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    const data = await res.json();

    if (data.success) {
      return {
        success: true,
        message: `Upvoted ${comment_id ? 'comment' : 'post'} ${post_id}`
      };
    } else {
      return {
        success: false,
        error: data.error,
        message: `Failed to upvote: ${data.error}`
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      message: `Error upvoting: ${error.message}`
    };
  }
}

// Main execution
const toolName = process.argv[2];
const params = JSON.parse(process.argv[3] || '{}');

switch (toolName) {
  case 'moltbook_check':
    checkMoltbook().then(result => console.log(JSON.stringify(result, null, 2)));
    break;
  case 'moltbook_post':
    createPost(params).then(result => console.log(JSON.stringify(result, null, 2)));
    break;
  case 'moltbook_comment':
    commentOnPost(params).then(result => console.log(JSON.stringify(result, null, 2)));
    break;
  case 'moltbook_upvote':
    upvotePost(params).then(result => console.log(JSON.stringify(result, null, 2)));
    break;
  default:
    console.error(JSON.stringify({
      success: false,
      error: `Unknown tool: ${toolName}`,
      available: ['moltbook_check', 'moltbook_post', 'moltbook_comment', 'moltbook_upvote']
    }));
}
